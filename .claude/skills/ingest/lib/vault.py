"""
vault.py — Cross-platform vault detection + DOI-based idempotency lookups.

Phase 2a core: find_note_by_doi + resolve_author_year_idempotent.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)


def find_vault() -> Path:
    """Cross-platform vault root detection.
    Priority: env > cwd/parents > platform defaults."""
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


def parse_frontmatter(path: Path) -> dict:
    """Parse frontmatter from a markdown file. Returns {} on error."""
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return {}
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"\'')
    return fm


def find_note_by_doi(vault: Path, doi: str) -> Optional[Path]:
    """Search 07-wiki/paper-notes/*.md for matching doi in frontmatter.
    Excludes _broken/. Returns Path or None.
    Idempotency core — Phase 2a."""
    if not doi:
        return None
    pn_dir = vault / '07-wiki' / 'paper-notes'
    if not pn_dir.is_dir():
        return None
    target = doi.lower().strip()
    for p in pn_dir.glob('*.md'):
        if '_broken' in p.parts:
            continue
        fm = parse_frontmatter(p)
        val = fm.get('doi', '').lower().strip()
        if val == target:
            return p
    return None


def resolve_author_year_idempotent(vault: Path, base: str, doi: str) -> Tuple[str, str]:
    """Return (author_year, action).
    action = 'update' if DOI matches existing note (base or suffixed)
    action = 'create' if new entry needed (base or next free suffix)

    Phase 2a core: DOI-first lookup BEFORE basename suffix resolution."""
    # 1. DOI-based lookup (primary)
    existing = find_note_by_doi(vault, doi)
    if existing:
        return existing.stem, 'update'

    # 2. Basename collision check
    pn_dir = vault / '07-wiki' / 'paper-notes'
    pn_dir.mkdir(parents=True, exist_ok=True)
    if not (pn_dir / f'{base}.md').exists():
        return base, 'create'

    # 3. Suffix resolution
    for suffix in 'bcdefghijklmnopqrstuvwxyz':
        candidate = f'{base}{suffix}'
        if not (pn_dir / f'{candidate}.md').exists():
            return candidate, 'create'

    raise RuntimeError(f'Too many basename collisions for {base}')


def is_confirmed(fm: dict) -> bool:
    """Phase 2a: CONFIRMED status must have slot + all required fields.
    Per Codex B8."""
    required = ['paper1_sections', 'paper1_slots', 'paper1_tier',
                'paper1_role', 'doi', 'ingest_agent']
    for key in required:
        val = fm.get(key)
        if not val or val in ('UNSET', 'TBD', 'candidate'):
            return False
    if fm.get('paper1_tier') not in ('A', 'B', 'C', 'D', 'E'):
        return False
    return True


def pending_has_doi(vault: Path, doi: str) -> bool:
    """Check if DOI already in _pending.md (idempotency).
    Returns True if row found."""
    pending = vault / '03-projects/Paper-1/references/_pending.md'
    if not pending.exists():
        return False
    try:
        text = pending.read_text(encoding='utf-8')
    except Exception:
        return False
    return doi.lower() in text.lower()


def refs_log_has_add(vault: Path, doi: str) -> bool:
    """Check if DOI already logged in refs-log.md as ADD."""
    log = vault / '03-projects/Paper-1/references/refs-log.md'
    if not log.exists():
        return False
    try:
        text = log.read_text(encoding='utf-8')
    except Exception:
        return False
    # Lines with ADD and DOI
    return f'ADD' in text and doi.lower() in text.lower()


if __name__ == '__main__':
    # Quick CLI for vault debugging
    try:
        v = find_vault()
        print(f'Vault: {v}')
        print(f'07-wiki/paper-notes/: {sum(1 for _ in (v/"07-wiki/paper-notes").glob("*.md") if "_broken" not in _.parts)} files')
        print(f'08-raw/papers/: {sum(1 for _ in (v/"08-raw/papers").glob("*.pdf"))} PDFs')
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)
