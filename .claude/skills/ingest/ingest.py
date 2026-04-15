#!/usr/bin/env python3
"""
ingest — Paper-aware Karpathy LLM Wiki Op #1

Fetches paper metadata, saves PDF to 08-raw/papers/, creates paper-note in
07-wiki/paper-notes/ with mode-appropriate depth, updates wiki cross-references,
appends index + log.

Modes: shallow / deep / paper1

Usage:
  ingest.py <source> [options]
  ingest.py 10.1016/j.ijfatigue.2008.07.002 --mode paper1 --section '§2.1' --tier A --role anchor
  ingest.py --watch --mode shallow --auto --quiet
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# Phase 2b: PDF fetch integration
sys.path.insert(0, str(Path(__file__).parent / 'lib'))
try:
    from pdf_fetch import fetch_pdf
    PDF_FETCH_AVAILABLE = True
except ImportError:
    PDF_FETCH_AVAILABLE = False


# -----------------------------
# Cross-platform vault detection
# -----------------------------
def find_vault():
    if v := os.environ.get('RESEARCH_VAULT'):
        p = Path(v).expanduser()
        if (p / 'CLAUDE.md').exists() and (p / '07-wiki').is_dir():
            return p

    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / 'CLAUDE.md').exists() and (parent / '07-wiki').is_dir():
            return parent

    import platform
    candidates = []
    if platform.system() == 'Darwin':
        candidates = [
            Path.home() / 'Documents/Research Vault',
            Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Research Vault',
        ]
    else:
        try:
            with open('/proc/version') as f:
                if 'microsoft' in f.read().lower():
                    import subprocess
                    r = subprocess.run(['cmd.exe', '/C', 'echo %USERNAME%'],
                                       capture_output=True, text=True, timeout=5)
                    candidates.append(Path(f'/mnt/c/Users/{r.stdout.strip()}/Documents/Research Vault'))
        except Exception:
            pass
        candidates.append(Path.home() / 'Documents/Research Vault')

    for c in candidates:
        if c.exists() and (c / 'CLAUDE.md').exists():
            return c
    raise RuntimeError('Vault not found. Set RESEARCH_VAULT env var.')


# -----------------------------
# Crossref
# -----------------------------
def fetch_crossref(doi):
    url = f'https://api.crossref.org/works/{urllib.parse.quote(doi, safe="/:()")}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'research-vault-ingest/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())['message']
    except Exception as e:
        return {'_error': str(e)}


def derive_author_year(meta):
    """Extract FirstAuthorLastName + Year from Crossref metadata."""
    authors = meta.get('author', [])
    year_parts = meta.get('issued', {}).get('date-parts', [[None]])
    year = year_parts[0][0] if year_parts and year_parts[0] else None
    if not authors or not year:
        return None
    last = authors[0].get('family', '').replace(' ', '').replace('-', '')
    return f'{last}{year}' if last and year else None


# -----------------------------
# Duplicate check + naming
# -----------------------------
def resolve_author_year(vault, base):
    """Handle AuthorYear, AuthorYearb, AuthorYearc collisions."""
    pn_dir = vault / '07-wiki' / 'paper-notes'
    pn_dir.mkdir(exist_ok=True)
    if not (pn_dir / f'{base}.md').exists():
        return base, False
    # exists — check if it's the same paper (by DOI in frontmatter) or different
    for suffix in 'bcdefgh':
        candidate = f'{base}{suffix}'
        if not (pn_dir / f'{candidate}.md').exists():
            return candidate, True  # new suffix required
    raise RuntimeError(f'Too many collisions for {base}')


# -----------------------------
# Paper-note generator
# -----------------------------
def generate_paper_note(meta, mode, vault, args, author_year):
    today = datetime.now().strftime('%Y-%m-%d')
    doi = meta.get('DOI', '').lower()
    title = ' '.join(meta.get('title', [''])).strip()
    authors_list = meta.get('author', [])
    first_author_last = authors_list[0].get('family', '') if authors_list else ''
    if len(authors_list) > 1:
        authors_str = f'{first_author_last} et al.'
    elif len(authors_list) == 1:
        g = authors_list[0].get('given', '')
        authors_str = f'{g} {first_author_last}'.strip()
    else:
        authors_str = ''
    year = meta.get('issued', {}).get('date-parts', [[None]])[0][0]
    journal = (meta.get('container-title') or [''])[0]
    volume = meta.get('volume', '')
    pages = meta.get('page', '')
    abstract = meta.get('abstract', '') or ''
    abstract = re.sub(r'<[^>]+>', '', abstract).strip()

    pdf_path_vault = f'08-raw/papers/{author_year}.pdf'
    pdf_available = (vault / pdf_path_vault).exists()
    oa_status = meta.get('_oa_status', 'unknown')

    # Frontmatter base
    fm = {
        'type': 'paper-note',
        'citation_key': author_year,
        'doi': doi,
        'title': title,
        'authors': authors_str,
        'year': year,
        'journal': journal,
        'volume': volume,
        'pages': pages,
        'aliases': [f'{first_author_last} {year}'],
        'pdf_path': pdf_path_vault,
        'pdf_available': pdf_available,
        'oa_status': oa_status,
        'ingest_date': today,
        'ingest_agent': args.agent,
        'ingest_mode': mode,
        'tags': ['research/paper', f'ingest-mode/{mode}'],
        'date_created': today,
        'date_updated': today,
        'description': title[:80] + ('...' if len(title) > 80 else ''),
        'source': f'https://doi.org/{doi}' if doi else '',
    }

    # Paper-1 classification (paper1 mode)
    if mode == 'paper1':
        fm['paper1_sections'] = [args.section] if args.section else []
        fm['paper1_slots'] = [args.slot] if args.slot else []
        fm['paper1_tier'] = args.tier or 'UNSET'
        fm['paper1_role'] = args.role or 'candidate'
        fm['paper1_status'] = 'CONFIRMED' if (args.section and args.tier and args.role) else 'CANDIDATE'
        fm['paper1_shared_sections'] = []
        # §4 specific
        if args.section and args.section.startswith('§4'):
            fm['dt_classification'] = args.dt_classification or 'TBD'
            if args.tier == 'D':
                fm['tier_d_mode'] = args.tier_d_mode or 'TBD'
            if args.wording_constraint:
                fm['wording_constraint'] = args.wording_constraint
        fm['tags'].append(f'paper-1/section-{args.section[1] if args.section else "N"}')
        if args.tier:
            fm['tags'].append(f'tier-{args.tier}')

    # Serialize frontmatter (simple YAML)
    fm_lines = ['---']
    for k, v in fm.items():
        if isinstance(v, list):
            fm_lines.append(f'{k}: {json.dumps(v, ensure_ascii=False)}')
        elif isinstance(v, bool):
            fm_lines.append(f'{k}: {"true" if v else "false"}')
        elif v is None or v == '':
            fm_lines.append(f'{k}: ""')
        else:
            sv = str(v).replace('"', '\\"')
            fm_lines.append(f'{k}: "{sv}"')
    fm_lines.append('---')

    # Body
    body = [
        f'# {title}',
        '',
        '## 논문 정보',
        f'- **Journal / Venue**: {journal} vol.{volume} ({year}){" pp. "+pages if pages else ""}',
        f'- **DOI**: [{doi}](https://doi.org/{doi})' if doi else '- **DOI**: (none)',
        f'- **Open access**: {oa_status}',
        f'- **PDF**: `{pdf_path_vault}`' + ('' if pdf_available else ' (NOT YET DOWNLOADED)'),
        '',
        '## Abstract',
        abstract if abstract else '(not available from metadata)',
        '',
    ]

    if mode == 'shallow':
        body.extend([
            '## Method',
            '(shallow ingest — method summary pending deep review)',
            '',
            '## Key Contribution',
            '(shallow ingest — contribution summary pending deep review)',
            '',
            '## Relevance',
            f'Ingested {today} in shallow mode for harvest. Re-ingest with `--mode deep` or `--mode paper1` for full analysis.',
            '',
        ])
    else:
        body.extend([
            '## 연구 배경',
            '(deep ingest — fill from PDF read)',
            '',
            '## 핵심 주장 / 기여',
            '1. (claim 1)',
            '2. (claim 2)',
            '',
            '## Method',
            '(method summary)',
            '',
            '## Verbatim Quotes',
            '> (important verbatim quotes, esp. canonical definitions or L-1 content)',
            '',
        ])

    if mode == 'paper1':
        section = args.section or '§N.M'
        body.extend([
            '## Paper-1 Usage',
            f'### {section}' + (f' {args.slot}' if args.slot else ''),
            f'- **Claim**: (what claim from this paper goes to {section})',
            f'- **Tier**: {args.tier or "TBD"} (근거: {args.tier_reason or "peer-reviewed venue"})',
            f'- **Role**: {args.role or "candidate"}',
            f'- **Wording discipline**: {args.wording_constraint or "standard"}',
            f'- **Hedging**: {"Tier D " + (args.tier_d_mode or "TBD") if args.tier == "D" else "none"}',
            '',
            '## Tier 근거',
            f'(1 paragraph — why Tier {args.tier or "TBD"} and reviewer defensibility)',
            '',
        ])

        if args.section and args.section.startswith('§4'):
            body.extend([
                '## DT Classification',
                f'- **Def-Moderate**: {args.dt_classification or "TBD (auto-detect pending)"}',
                '- **근거**: (본문에서 이 분류를 뒷받침하는 부분)',
                '',
            ])
            if args.tier == 'D':
                body.extend([
                    '## H-Moderate',
                    '- **Body count**: (verifiable fact)',
                    '- **Footnote metric**: (unverifiable performance metric)',
                    '',
                ])

    body.extend([
        '## Limitations',
        '- (paper-acknowledged)',
        '- (Paper-1 perspective)' if mode == 'paper1' else '',
        '',
        '## Cross-references',
        '- **Entities**: (fill after ingest cross-cutting pass)',
        '- **Concepts**: ',
        '- **Syntheses**: ',
        '- **Related papers**: ',
        '',
        '## Ingest audit',
        f'- {today} ingest {args.agent} --mode {mode}' + (
            f' --section {args.section} --tier {args.tier} --role {args.role}' if mode == 'paper1' else ''),
        '',
    ])

    return '\n'.join(fm_lines) + '\n\n' + '\n'.join(body)


# -----------------------------
# Index + Log updates
# -----------------------------
def append_index(vault, author_year, description):
    idx = vault / '07-wiki' / 'index.md'
    if not idx.exists():
        return
    text = idx.read_text(encoding='utf-8')
    line = f'- [[{author_year}]] — {description}'
    if line in text:
        return
    # Insert under ## Paper-notes section
    if '## Paper-notes' in text:
        parts = text.split('## Paper-notes', 1)
        # find next ## after paper-notes section
        rest = parts[1]
        next_h2 = re.search(r'\n## ', rest)
        if next_h2:
            before = rest[:next_h2.start()]
            after = rest[next_h2.start():]
            new_rest = before.rstrip() + f'\n{line}\n' + after
        else:
            new_rest = rest.rstrip() + f'\n{line}\n'
        text = parts[0] + '## Paper-notes' + new_rest
    else:
        text = text.rstrip() + f'\n\n## Paper-notes\n{line}\n'
    idx.write_text(text, encoding='utf-8')


def append_log(vault, author_year, mode, agent, extras=''):
    log = vault / '07-wiki' / 'log.md'
    if not log.exists():
        return
    today = datetime.now().strftime('%Y-%m-%d')
    entry = f'\n## [{today}] ingest | {author_year} | {agent}\nMode: {mode}. {extras}\n'
    with log.open('a', encoding='utf-8') as f:
        f.write(entry)


# -----------------------------
# Paper-1 PROTOCOL integration
# -----------------------------
def append_paper1_pending(vault, author_year, doi, args):
    if args.mode != 'paper1':
        return
    pending = vault / '03-projects/Paper-1/references/_pending.md'
    if not pending.exists():
        return
    today = datetime.now().strftime('%Y-%m-%d')
    wikilink = f'[[{author_year}]]'
    section = args.section or 'TBD'
    reason = args.tier_reason or 'ingested via /ingest --mode paper1'
    status = 'CLAIMED' if (args.section and args.tier and args.role) else 'DRAFT'
    row = f'| {today} | {args.agent} | {doi} | {wikilink} | {section} | {reason} | {status} | — |'
    text = pending.read_text(encoding='utf-8')
    # Insert below the empty placeholder row, or at end of 현재 대기열 table
    placeholder = '| _(비어있음)_ | | | | | | | |'
    if placeholder in text:
        text = text.replace(placeholder, row)
    else:
        # append at end of 현재 대기열 table
        text = text.rstrip() + '\n' + row + '\n'
    pending.write_text(text, encoding='utf-8')


def append_paper1_refs_log(vault, author_year, args):
    if args.mode != 'paper1':
        return
    log = vault / '03-projects/Paper-1/references/refs-log.md'
    if not log.exists():
        return
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    extras = f'--section {args.section} --tier {args.tier} --role {args.role}' if args.section else 'DRAFT'
    entry = f'{now} | {args.agent} | ADD          | {author_year}              | /ingest mode=paper1 {extras}'
    with log.open('a', encoding='utf-8') as f:
        f.write('\n' + entry + '\n')


# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', nargs='?', help='DOI or URL or PDF path')
    ap.add_argument('--mode', choices=['shallow', 'deep', 'paper1'], default='shallow')
    ap.add_argument('--section', help="Paper-1 section (e.g. '§2.1', '§4.3')")
    ap.add_argument('--slot', help="Paper-1 slot (e.g. '§4.3 P2')")
    ap.add_argument('--tier', choices=['A', 'B', 'C', 'D', 'E'])
    ap.add_argument('--role', choices=['anchor', 'bridge', 'context', 'hedge', 'self-cite', 'open-slot'])
    ap.add_argument('--tier-reason', help='reason for tier classification (reviewer defensibility)')
    ap.add_argument('--dt-classification', choices=['DT', 'SHM-only', 'not-DT'])
    ap.add_argument('--tier-d-mode', choices=['body-count', 'footnote', 'context'])
    ap.add_argument('--wording-constraint', choices=['L-1', 'canonical', 'none'])
    ap.add_argument('--agent', default='cron', help='agent id (cron/§N-agent/user)')
    ap.add_argument('--force', action='store_true', help='re-ingest even if exists')
    ap.add_argument('--watch', action='store_true', help='inbox sweep mode')
    ap.add_argument('--auto', action='store_true', help='non-interactive')
    ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--no-pdf', action='store_true', help='skip PDF download (Phase 2b)')
    ap.add_argument('--pdf-max-mb', type=int, default=50, help='PDF size limit MB (default 50)')
    ap.add_argument('--manual-author', help='manual AuthorLastName override')
    ap.add_argument('--manual-year', type=int, help='manual year override')
    args = ap.parse_args()

    try:
        vault = find_vault()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(2)

    if not args.quiet:
        print(f'Vault: {vault}')

    if args.watch:
        # 01-inbox sweep
        inbox = vault / '01-inbox'
        count = 0
        for f in inbox.glob('*.pdf'):
            if not args.quiet:
                print(f'Watch: found {f.name} — skipped (manual ingest required for now)')
            # Full watch implementation requires PDF metadata extraction — defer
            count += 1
        if not args.quiet:
            print(f'Watch: {count} PDF(s) in inbox (automatic ingest not yet implemented; use manual /ingest <pdf>)')
        sys.exit(0)

    if not args.source:
        print('ERROR: source required (DOI/URL/PDF)', file=sys.stderr)
        sys.exit(2)

    # Determine source type
    src = args.source
    if re.match(r'^10\.\d+/', src):
        doi = src
    elif src.startswith('doi:'):
        doi = src[4:]
    else:
        print(f'ERROR: URL/PDF mode not fully implemented; use DOI for now', file=sys.stderr)
        sys.exit(2)

    if not args.quiet:
        print(f'DOI: {doi}')
        print(f'Mode: {args.mode}')

    # Fetch metadata
    meta = fetch_crossref(doi)
    if '_error' in meta:
        print(f'Crossref error: {meta["_error"]}', file=sys.stderr)
        sys.exit(2)

    # Derive AuthorYear
    author_year = args.manual_author + str(args.manual_year) if args.manual_author and args.manual_year else derive_author_year(meta)
    if not author_year:
        print('ERROR: could not derive AuthorYear from metadata. Use --manual-author + --manual-year', file=sys.stderr)
        sys.exit(2)

    # Handle collision
    base = author_year
    author_year, collided = resolve_author_year(vault, base)
    if collided and not args.force:
        if not args.quiet:
            print(f'Note: {base} exists — using {author_year}')

    # Phase 2b: PDF download (before note generation so pdf_available is accurate)
    if not args.no_pdf and PDF_FETCH_AVAILABLE:
        pdf_dest = vault / '08-raw' / 'papers' / f'{author_year}.pdf'
        ok, reason = fetch_pdf(doi, meta, pdf_dest, max_size_mb=args.pdf_max_mb)
        if not args.quiet:
            status = '✓' if ok else '✗'
            print(f'PDF {status}: {reason}')
        # meta used by generate_paper_note() — pass pdf status via _oa_status hint
        # (frontmatter will reflect real file existence via pdf_available check in generate_paper_note)
    elif args.no_pdf and not args.quiet:
        print('PDF: skipped (--no-pdf)')

    # Generate paper-note
    note = generate_paper_note(meta, args.mode, vault, args, author_year)
    note_path = vault / '07-wiki' / 'paper-notes' / f'{author_year}.md'
    note_path.write_text(note, encoding='utf-8')
    if not args.quiet:
        print(f'Paper-note: {note_path}')

    # Index + log
    desc = (meta.get('title', [''])[0] or '')[:80]
    append_index(vault, author_year, desc)
    append_log(vault, author_year, args.mode, args.agent,
               extras=f'PDF: {"available" if (vault/"08-raw/papers"/f"{author_year}.pdf").exists() else "n/a"}. Section: {args.section or "-"}. Tier: {args.tier or "-"}.')

    # Paper-1 PROTOCOL integration
    if args.mode == 'paper1':
        append_paper1_pending(vault, author_year, doi, args)
        append_paper1_refs_log(vault, author_year, args)
        if not args.quiet:
            print(f'Paper-1: _pending.md + refs-log.md updated')

    if not args.quiet:
        print(f'Done: {author_year} ingested ({args.mode} mode)')


if __name__ == '__main__':
    main()
