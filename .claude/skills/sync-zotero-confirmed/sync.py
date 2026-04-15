#!/usr/bin/env python3
"""
sync-zotero-confirmed — Confirm-time Zotero sync (Phase 2a-z).

Scans 07-wiki/paper-notes/*.md, filters CONFIRMED+slot, syncs to Zotero
with chapter collection assignment. Per Paper-1 PROTOCOL §8.

Usage:
  sync.py                          # dry-run
  sync.py --apply                  # actually sync
  sync.py --apply --pattern §4.*   # only §4 papers
  sync.py --apply --attach-pdf     # also PDF attachment (default off)

Exit codes:
  0 success, 1 partial, 2 error
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Import vault.py from ingest skill
INGEST_LIB = Path(__file__).resolve().parent.parent / 'ingest' / 'lib'
sys.path.insert(0, str(INGEST_LIB))

from vault import find_vault, parse_frontmatter, is_confirmed  # noqa: E402


# Chapter collection mapping
DEFAULT_CHAPTER_COLLECTIONS = {
    '§1': 'ICDZS7UB',  # Ch.1 Introduction
    '§2': 'CKMC5AWI',  # Ch.2 Classical Methods
    '§3': '726X7VBU',  # Ch.3 AI-Enhanced
    '§4': 'CB59XCM8',  # Ch.4 Digital Twin
    '§5': 'A5D2JZD4',  # Ch.5 Synthesis Roadmap
}


def load_chapter_collections():
    """Env override first, then defaults."""
    result = {}
    for sec in ('§1', '§2', '§3', '§4', '§5'):
        env_key = f'ZOTERO_CH_{sec[1]}_KEY'
        result[sec] = os.environ.get(env_key, DEFAULT_CHAPTER_COLLECTIONS[sec])
    return result


def get_zotero_client():
    """Returns zotero.Zotero client or None if env missing."""
    user_id = os.environ.get('ZOTERO_USER_ID')
    api_key = os.environ.get('ZOTERO_API_KEY')
    if not user_id or not api_key:
        return None
    try:
        from pyzotero import zotero
    except ImportError:
        print('ERROR: pyzotero not installed. pip install pyzotero', file=sys.stderr)
        return None
    return zotero.Zotero(user_id, 'user', api_key)


def find_by_doi(zot, doi):
    """Return item_key if DOI exists in Zotero library, else None."""
    if not doi:
        return None
    try:
        results = zot.items(q=doi, qmode='everything', limit=20)
        doi_lower = doi.lower().strip()
        for it in results:
            item_doi = (it['data'].get('DOI') or '').lower().strip()
            if item_doi == doi_lower:
                return it['data']['key']
    except Exception as e:
        print(f'  WARN: Zotero search error for {doi}: {e}', file=sys.stderr)
    return None


def fetch_crossref(doi):
    """Fetch Crossref metadata for DOI."""
    import urllib.parse
    import urllib.request
    url = f'https://api.crossref.org/works/{urllib.parse.quote(doi, safe="/:()")}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'research-vault-sync/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())['message']
    except Exception as e:
        return {'_error': str(e)}


def create_item_from_crossref(zot, meta):
    """Create Zotero item from Crossref metadata. Returns item_key or None."""
    if '_error' in meta:
        return None
    ct = meta.get('type', 'journal-article')
    it_type = {
        'book': 'book', 'monograph': 'book', 'edited-book': 'book',
        'book-chapter': 'bookSection',
        'proceedings-article': 'conferencePaper',
    }.get(ct, 'journalArticle')

    try:
        tmpl = zot.item_template(it_type)
    except Exception as e:
        print(f'  WARN: item_template failed: {e}', file=sys.stderr)
        return None

    tmpl['DOI'] = meta.get('DOI', '')
    tmpl['title'] = ' '.join(meta.get('title', [''])) or ''
    authors = []
    for a in meta.get('author', []):
        authors.append({
            'creatorType': 'author',
            'firstName': a.get('given', ''),
            'lastName': a.get('family', ''),
        })
    if authors:
        tmpl['creators'] = authors
    if meta.get('issued', {}).get('date-parts'):
        y = meta['issued']['date-parts'][0]
        tmpl['date'] = '-'.join(str(x) for x in y)
    if meta.get('container-title') and it_type == 'journalArticle':
        tmpl['publicationTitle'] = meta['container-title'][0]
    for k in ('volume', 'issue', 'publisher'):
        if meta.get(k):
            tmpl[k] = meta[k]
    if meta.get('page'):
        tmpl['pages'] = meta['page']
    if meta.get('ISSN'):
        tmpl['ISSN'] = ','.join(meta['ISSN'])

    try:
        result = zot.create_items([tmpl])
        if result.get('successful'):
            return list(result['successful'].values())[0]['data']['key']
    except Exception as e:
        print(f'  WARN: create_items failed: {e}', file=sys.stderr)
    return None


def assign_to_chapter(zot, item_key, section, chapter_collections):
    """Use addto_collection() per Codex B5. Additive (idempotent)."""
    ch_key = chapter_collections.get(section[:2])
    if not ch_key:
        return False
    try:
        item = zot.item(item_key)
        existing_colls = item['data'].get('collections', [])
        if ch_key in existing_colls:
            return True  # already assigned
        # use update_item with added collection (pyzotero 1.11.0 way)
        item['data']['collections'] = existing_colls + [ch_key]
        return bool(zot.update_item(item))
    except Exception as e:
        print(f'  WARN: assign_to_chapter failed ({section}): {e}', file=sys.stderr)
        return False


def attach_pdf(zot, item_key, pdf_path):
    """Attach PDF as child item. Skip if already present."""
    try:
        existing = zot.children(item_key)
        for c in existing:
            if c['data'].get('title') == pdf_path.name or \
               c['data'].get('filename') == pdf_path.name:
                return True  # already attached
        zot.attachment_simple([str(pdf_path)], item_key)
        return True
    except Exception as e:
        print(f'  WARN: attach_pdf failed: {e}', file=sys.stderr)
        return False


def scan_confirmed(vault, pattern=None):
    """Return list of (path, frontmatter) for CONFIRMED notes matching pattern."""
    pn_dir = vault / '07-wiki' / 'paper-notes'
    confirmed = []
    for p in pn_dir.glob('*.md'):
        if '_broken' in p.parts:
            continue
        fm = parse_frontmatter(p)
        if not is_confirmed(fm):
            continue
        # parse paper1_sections (string or list)
        secs = fm.get('paper1_sections', '')
        if isinstance(secs, str):
            # try JSON decode
            try:
                secs = json.loads(secs) if secs.startswith('[') else [secs]
            except Exception:
                secs = [secs]
        if pattern:
            if not any(re.match(pattern.replace('*', '.*'), s) for s in secs if s):
                continue
        fm['_parsed_sections'] = secs
        confirmed.append((p, fm))
    return confirmed


def update_frontmatter(path, updates):
    """Update frontmatter fields in a md file."""
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not m:
        return False
    fm_text = m.group(1)
    body = m.group(2)
    for k, v in updates.items():
        val = f'"{v}"' if not isinstance(v, (int, float, bool)) else str(v)
        line = f'{k}: {val}'
        if re.search(rf'^{re.escape(k)}:\s*.*$', fm_text, re.M):
            fm_text = re.sub(rf'^{re.escape(k)}:\s*.*$', line, fm_text, flags=re.M)
        else:
            fm_text += f'\n{line}'
    new_text = f'---\n{fm_text}\n---\n{body}'
    path.write_text(new_text, encoding='utf-8')
    return True


def append_log(vault, count, agent='sync-zotero-confirmed'):
    log = vault / '07-wiki' / 'log.md'
    if not log.exists():
        return
    today = datetime.now().strftime('%Y-%m-%d')
    entry = f'\n## [{today}] zotero-sync | {count} papers | {agent}\nsync-zotero-confirmed skill executed.\n'
    with log.open('a', encoding='utf-8') as f:
        f.write(entry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='actually sync (default: dry-run)')
    ap.add_argument('--pattern', help="section pattern (e.g. '§4.*')")
    ap.add_argument('--attach-pdf', action='store_true', help='also attach PDF')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--agent', default='sync-zotero-confirmed', help='agent id')
    args = ap.parse_args()

    try:
        vault = find_vault()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(2)

    if not args.quiet:
        print(f'Vault: {vault}')
        print(f'Mode: {"APPLY" if args.apply else "dry-run"}')
        if args.pattern:
            print(f'Pattern: {args.pattern}')
        print()

    # 1. Scan
    confirmed = scan_confirmed(vault, pattern=args.pattern)
    if not args.quiet:
        print(f'Found {len(confirmed)} CONFIRMED + slot paper-notes')

    if not args.apply:
        # dry-run
        for p, fm in confirmed:
            secs = fm.get('_parsed_sections', [])
            print(f'  - {p.stem} — sections={secs} — zotero_key={fm.get("zotero_key", "none")}')
        print(f'\nDry-run complete. --apply to execute.')
        sys.exit(0)

    # 2. Sync
    zot = get_zotero_client()
    if not zot:
        print('ERROR: Zotero env not set (ZOTERO_USER_ID + ZOTERO_API_KEY)', file=sys.stderr)
        sys.exit(2)

    chapter_collections = load_chapter_collections()
    synced = 0
    failed = 0

    for p, fm in confirmed:
        doi = fm.get('doi', '').strip()
        if not doi:
            failed += 1
            continue

        if not args.quiet:
            print(f'  [{p.stem}] DOI={doi}')

        # find or create
        item_key = find_by_doi(zot, doi)
        if not item_key:
            meta = fetch_crossref(doi)
            if '_error' in meta:
                if not args.quiet:
                    print(f'    Crossref fail: {meta["_error"]}')
                failed += 1
                continue
            item_key = create_item_from_crossref(zot, meta)
            if not item_key:
                failed += 1
                continue
            if not args.quiet:
                print(f'    Created [{item_key}]')
        else:
            if not args.quiet:
                print(f'    Found existing [{item_key}]')

        # assign to chapters
        sections = fm.get('_parsed_sections', [])
        shared = fm.get('paper1_shared_sections', [])
        if isinstance(shared, str):
            try:
                shared = json.loads(shared) if shared.startswith('[') else [shared]
            except Exception:
                shared = []
        all_sections = list(sections) + list(shared)
        for sec in all_sections:
            if sec:
                assign_to_chapter(zot, item_key, sec, chapter_collections)

        # attach PDF if requested
        pdf_path_str = fm.get('pdf_path', '')
        if args.attach_pdf and pdf_path_str:
            pdf_path = vault / pdf_path_str
            if pdf_path.exists():
                attach_pdf(zot, item_key, pdf_path)

        # update frontmatter
        updates = {
            'zotero_key': item_key,
            'date_updated': datetime.now().strftime('%Y-%m-%d'),
        }
        update_frontmatter(p, updates)

        synced += 1
        # pyzotero handles its own backoff; no extra sleep

    append_log(vault, synced, args.agent)

    if not args.quiet:
        print(f'\nSynced: {synced}, Failed: {failed}')

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
