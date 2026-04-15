"""
pdf_fetch.py — PDF download with fallback chain (Phase 2b).

Order:
  1. Unpaywall API (open access PDF URL)
  2. Crossref link-set (content-type: application/pdf)
  3. arXiv direct (if arxiv DOI)

Validation:
  - HTTP 200
  - Size <= max_size_mb (default 50)
  - First 4 bytes == b'%PDF' (magic number)

Idempotent: if dest exists + valid PDF, skip download.
Vault-only by default. No Zotero attachment (Codex B7).
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

UA = os.environ.get('INGEST_USER_AGENT', 'research-vault-ingest/1.0 (+mailto:hyeonseok@gist.ac.kr)')
EMAIL = os.environ.get('UNPAYWALL_EMAIL', 'hyeonseok@gist.ac.kr')
MAX_SIZE_MB = int(os.environ.get('INGEST_MAX_PDF_MB', '50'))
MAGIC_PDF = b'%PDF'


def _http_get(url, timeout=20, accept='application/json'):
    """GET with UA + Accept header. Returns (status, body_bytes) or raises."""
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def try_unpaywall(doi: str) -> Optional[str]:
    """Query Unpaywall for OA PDF URL. Returns URL or None."""
    if not doi or not doi.startswith('10.'):
        return None
    quoted = urllib.parse.quote(doi, safe='/:()')
    url = f'https://api.unpaywall.org/v2/{quoted}?email={urllib.parse.quote(EMAIL)}'
    try:
        status, body = _http_get(url, timeout=20)
        if status != 200:
            return None
        data = json.loads(body)
        best = data.get('best_oa_location') or {}
        pdf_url = best.get('url_for_pdf')
        if pdf_url:
            return pdf_url
        # fallback to landing URL if pdf URL missing but OA
        for loc in data.get('oa_locations', []):
            if u := loc.get('url_for_pdf'):
                return u
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        pass
    return None


def try_crossref_link(meta: dict) -> Optional[str]:
    """Extract application/pdf URL from Crossref link-set."""
    for link in (meta or {}).get('link', []):
        if link.get('content-type') == 'application/pdf':
            u = link.get('URL')
            if u:
                return u
    return None


def try_arxiv(doi: str) -> Optional[str]:
    """arXiv direct PDF URL for 10.48550/arxiv.* or arXiv-style DOI."""
    if not doi:
        return None
    # 10.48550/arxiv.2403.xxxxx
    m = re.match(r'10\.48550/arxiv\.(\S+)', doi, re.I)
    if m:
        arxiv_id = m.group(1)
        return f'https://arxiv.org/pdf/{arxiv_id}.pdf'
    # arXiv ID pattern (no DOI prefix)
    m = re.match(r'^(\d{4}\.\d{4,5}(?:v\d+)?)$', doi)
    if m:
        return f'https://arxiv.org/pdf/{m.group(1)}.pdf'
    return None


def validate_pdf(path: Path) -> bool:
    """Magic number + non-empty check."""
    try:
        if path.stat().st_size < 1024:  # <1KB likely error page
            return False
        with path.open('rb') as f:
            head = f.read(4)
        return head == MAGIC_PDF
    except Exception:
        return False


def download_pdf(url: str, dest: Path, max_size_mb: int = MAX_SIZE_MB, timeout: int = 30) -> Tuple[bool, str]:
    """Stream download with size + magic number validation.
    Returns (success, reason)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.partial')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/pdf,*/*'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return False, f'HTTP {r.status}'
            # Content-Length guard
            cl = r.headers.get('Content-Length')
            if cl and int(cl) > max_size_mb * 1024 * 1024:
                return False, f'too large: {int(cl) / 1024 / 1024:.1f}MB > {max_size_mb}MB'
            # Stream to temp
            bytes_read = 0
            max_bytes = max_size_mb * 1024 * 1024
            with tmp.open('wb') as f:
                while True:
                    chunk = r.read(64 * 1024)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    if bytes_read > max_bytes:
                        f.close()
                        tmp.unlink(missing_ok=True)
                        return False, f'stream exceeded {max_size_mb}MB'
                    f.write(chunk)
        # Validate
        if not validate_pdf(tmp):
            tmp.unlink(missing_ok=True)
            return False, 'invalid PDF (magic number or too small)'
        tmp.rename(dest)
        return True, f'ok ({bytes_read / 1024:.1f}KB)'
    except urllib.error.HTTPError as e:
        tmp.unlink(missing_ok=True)
        return False, f'HTTP error {e.code}'
    except urllib.error.URLError as e:
        tmp.unlink(missing_ok=True)
        return False, f'network error: {e.reason}'
    except Exception as e:
        tmp.unlink(missing_ok=True)
        return False, f'unexpected: {e}'


def fetch_pdf(doi: str, crossref_meta: dict, dest: Path, max_size_mb: int = MAX_SIZE_MB) -> Tuple[bool, str]:
    """Orchestrator: Unpaywall → Crossref link → arXiv → fail.
    Idempotent: if dest exists + valid, skip.
    Returns (success, reason)."""
    # Idempotent check
    if dest.exists():
        if validate_pdf(dest):
            return True, 'already exists (valid)'
        # invalid → delete + retry
        dest.unlink(missing_ok=True)

    attempts = []

    # 1. Unpaywall
    url = try_unpaywall(doi)
    if url:
        ok, reason = download_pdf(url, dest, max_size_mb)
        attempts.append(f'unpaywall: {reason}')
        if ok:
            return True, f'unpaywall ({reason})'

    # 2. Crossref link-set
    url = try_crossref_link(crossref_meta)
    if url:
        ok, reason = download_pdf(url, dest, max_size_mb)
        attempts.append(f'crossref: {reason}')
        if ok:
            return True, f'crossref-link ({reason})'

    # 3. arXiv
    url = try_arxiv(doi)
    if url:
        ok, reason = download_pdf(url, dest, max_size_mb)
        attempts.append(f'arxiv: {reason}')
        if ok:
            return True, f'arxiv ({reason})'

    return False, 'all failed: ' + '; '.join(attempts) if attempts else 'no PDF URL found'


if __name__ == '__main__':
    # CLI smoke test
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('doi')
    ap.add_argument('--out', default='/tmp/test.pdf')
    ap.add_argument('--max-mb', type=int, default=MAX_SIZE_MB)
    args = ap.parse_args()

    # Get Crossref meta for link-set
    try:
        url = f'https://api.crossref.org/works/{urllib.parse.quote(args.doi, safe="/:()")}'
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            meta = json.loads(r.read())['message']
    except Exception as e:
        print(f'Crossref fetch failed: {e}', file=sys.stderr)
        meta = {}

    ok, reason = fetch_pdf(args.doi, meta, Path(args.out), args.max_mb)
    print(f'{"OK" if ok else "FAIL"}: {reason}')
    if ok:
        print(f'Saved: {args.out}')
    sys.exit(0 if ok else 1)
