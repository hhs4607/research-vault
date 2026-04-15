#!/usr/bin/env python3
"""
wiki-lint — Research Vault 07-wiki/ health check

Karpathy LLM Wiki pattern operation #3: Lint
Runs non-interactive, cron-safe. Writes report + log.md append.

Usage:
  python3 wiki_lint.py                          # default report path
  python3 wiki_lint.py --fix                    # auto-fix safe violations
  python3 wiki_lint.py --report path/to/out.md  # custom report path
  python3 wiki_lint.py --quiet                  # no stdout

Exit codes:
  0 : no high-severity issues
  1 : high-severity issues found
  2 : execution error
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def find_vault():
    """Cross-platform vault root detection."""
    if v := os.environ.get('RESEARCH_VAULT'):
        p = Path(v).expanduser()
        if (p / 'CLAUDE.md').exists() and (p / '07-wiki').is_dir():
            return p

    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (parent / 'CLAUDE.md').exists() and (parent / '07-wiki').is_dir():
            return parent

    import platform
    system = platform.system()
    candidates = []
    if system == 'Darwin':
        candidates = [
            Path.home() / 'Documents/Research Vault',
            Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Research Vault',
        ]
    elif system == 'Linux':
        # WSL check
        try:
            with open('/proc/version') as f:
                is_wsl = 'microsoft' in f.read().lower()
        except Exception:
            is_wsl = False
        if is_wsl:
            try:
                import subprocess
                r = subprocess.run(['cmd.exe', '/C', 'echo %USERNAME%'],
                                   capture_output=True, text=True, timeout=5)
                win_user = r.stdout.strip()
                candidates.append(Path(f'/mnt/c/Users/{win_user}/Documents/Research Vault'))
            except Exception:
                pass
        candidates.append(Path.home() / 'Documents/Research Vault')
        candidates.append(Path.home() / 'Research Vault')

    for c in candidates:
        if c.exists() and (c / 'CLAUDE.md').exists():
            return c
    raise RuntimeError("Research Vault not found. Set RESEARCH_VAULT env var.")


FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
WIKILINK_RE = re.compile(r'\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]')
PAPER_NOTE_PATTERN = re.compile(r'^[A-Z][a-zA-Z]+[0-9]{4}[a-z]?\.md$')


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"\'')
    return fm


def build_index(vault):
    """Collect all md files with metadata for xref resolution."""
    files_by_basename = {}  # basename (w/o .md) -> list of Path
    all_md = []
    for p in vault.rglob('*.md'):
        # skip .obsidian, archives, raw drafts for primary index (but track)
        if any(part.startswith('.') for part in p.parts):
            continue
        all_md.append(p)
        base = p.stem
        files_by_basename.setdefault(base, []).append(p)
    return all_md, files_by_basename


def check_wiki(vault, fix=False):
    """Run all checks. Return list of (severity, file, issue, suggested_action)."""
    findings = []
    wiki = vault / '07-wiki'
    raw = vault / '08-raw'

    if not wiki.is_dir():
        findings.append(('high', str(wiki), '07-wiki/ directory missing', 'create per _protocol'))
        return findings

    all_md, idx = build_index(vault)

    # === Check 1: frontmatter type: field (wiki pages only) ===
    for p in wiki.rglob('*.md'):
        if '_broken' in p.parts or p.name in ('index.md', 'log.md', '_protocol.md'):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception as e:
            findings.append(('high', str(p), f'read error: {e}', 'inspect manually'))
            continue
        fm = parse_frontmatter(text)
        if 'type' not in fm:
            # infer from folder
            folder = p.relative_to(wiki).parts[0] if p.parent != wiki else 'root'
            type_guess = {
                'paper-notes': 'paper-note',
                'entities': 'entity',
                'concepts': 'concept',
                'comparisons': 'comparison',
                'syntheses': 'synthesis',
            }.get(folder)
            findings.append(('high', str(p.relative_to(vault)),
                           f"frontmatter missing 'type:' (expected: {type_guess or 'unknown'})",
                           f'add `type: {type_guess}` to frontmatter' if type_guess else 'review'))

    # === Check 2: broken wikilinks ===
    for p in wiki.rglob('*.md'):
        if '_broken' in p.parts:
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip()
            # 정확 basename or path 체크
            target_base = target.split('/')[-1]
            if target_base not in idx:
                findings.append(('high', str(p.relative_to(vault)),
                               f'broken wikilink: [[{target}]]',
                               'fix target or create page'))

    # === Check 3: orphan pages (non-paper-notes) ===
    # Build inbound count
    inbound = {}
    for p in all_md:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in WIKILINK_RE.finditer(text):
            target_base = m.group(1).split('/')[-1].strip()
            inbound[target_base] = inbound.get(target_base, 0) + 1

    for p in wiki.rglob('*.md'):
        if '_broken' in p.parts or p.name in ('index.md', 'log.md', '_protocol.md'):
            continue
        # paper-notes 은 orphan 허용 (synthesis 에서 선택적으로 link)
        if 'paper-notes' in p.parts:
            continue
        if inbound.get(p.stem, 0) == 0:
            findings.append(('medium', str(p.relative_to(vault)),
                           'orphan page (0 inbound wikilinks)',
                           'add link from relevant synthesis/concept or deprecate'))

    # === Check 4: paper-note naming violations ===
    pn_dir = wiki / 'paper-notes'
    if pn_dir.is_dir():
        for p in pn_dir.iterdir():
            if p.is_dir() or p.name.startswith('.') or p.name.startswith('_'):
                continue
            if not PAPER_NOTE_PATTERN.match(p.name):
                findings.append(('medium', str(p.relative_to(vault)),
                               f'paper-note naming violation (expected AuthorYear[a-z]?.md): {p.name}',
                               'rename or move to _broken/ for review'))

    # === Check 5: index.md coverage ===
    idx_file = wiki / 'index.md'
    if idx_file.exists():
        idx_text = idx_file.read_text(encoding='utf-8')
        idx_links = set(m.group(1).split('/')[-1].strip()
                       for m in WIKILINK_RE.finditer(idx_text))
        for p in wiki.rglob('*.md'):
            if '_broken' in p.parts or p.name in ('index.md', 'log.md', '_protocol.md'):
                continue
            # paper-notes 는 개별 listing 대신 폴더로 aggregate 가능 (index에 섹션 pointer면 OK)
            if 'paper-notes' in p.parts:
                continue
            if p.stem not in idx_links:
                findings.append(('low', str(p.relative_to(vault)),
                               f"page not listed in index.md: [[{p.stem}]]",
                               'add entry to appropriate index section'))

    # === Check 6: 08-raw 위반 (paper-notes 나 해석-성 md 발견) ===
    if raw.is_dir():
        for p in raw.rglob('*.md'):
            if p.name in ('_protocol.md', 'MOC.md'):
                continue
            if 'draft-lineage' in p.parts or 'kakao-archive' in p.parts:
                continue
            findings.append(('high', str(p.relative_to(vault)),
                           'unexpected .md in 08-raw/ (violates raw immutability, interpreted data belongs in 07-wiki/)',
                           'move to 07-wiki/ or add to draft-lineage/kakao-archive if raw'))

    # === Check 7: log.md stale ===
    log_file = wiki / 'log.md'
    if log_file.exists():
        log_text = log_file.read_text(encoding='utf-8')
        dates = re.findall(r'## \[(\d{4}-\d{2}-\d{2})\]', log_text)
        if dates:
            last = max(dates)
            last_dt = datetime.strptime(last, '%Y-%m-%d')
            days = (datetime.now() - last_dt).days
            if days > 30:
                findings.append(('low', '07-wiki/log.md',
                               f'last log entry {days} days ago ({last})',
                               'if active, append recent activity'))

    # === Auto-fix (--fix mode) ===
    fixes_applied = []
    if fix:
        for severity, file, issue, action in findings:
            if 'frontmatter missing' in issue and 'add `type:' in action:
                # try to insert type into frontmatter
                path = vault / file
                try:
                    text = path.read_text(encoding='utf-8')
                    m = FRONTMATTER_RE.match(text)
                    type_val = re.search(r'type: (\w+[-\w]*)', action)
                    if m and type_val:
                        new_fm = m.group(1) + f'\ntype: {type_val.group(1)}'
                        new_text = text.replace(m.group(1), new_fm, 1)
                        path.write_text(new_text, encoding='utf-8')
                        fixes_applied.append(f'fixed type in {file}')
                except Exception as e:
                    fixes_applied.append(f'fix error {file}: {e}')

    return findings, fixes_applied


def write_report(vault, findings, fixes_applied, report_path=None):
    today = datetime.now().strftime('%Y-%m-%d')
    if report_path is None:
        report_path = vault / '07-wiki' / f'lint-report-{today}.md'
    else:
        report_path = Path(report_path)

    high = [f for f in findings if f[0] == 'high']
    med = [f for f in findings if f[0] == 'medium']
    low = [f for f in findings if f[0] == 'low']

    lines = [
        f'---',
        f'title: "Wiki Lint Report — {today}"',
        f'date: {today}',
        f'tags: [meta/lint, wiki]',
        f'description: "Automated wiki-lint report. {len(high)} high / {len(med)} medium / {len(low)} low."',
        f'---',
        f'',
        f'# Wiki Lint Report — {today}',
        f'',
        f'**Summary**: {len(high)} high / {len(med)} medium / {len(low)} low findings.',
        f'',
    ]

    if fixes_applied:
        lines.append('## Auto-fixes applied')
        for fx in fixes_applied:
            lines.append(f'- {fx}')
        lines.append('')

    for label, items in [('High Severity', high), ('Medium Severity', med), ('Low Severity', low)]:
        if not items:
            continue
        lines.append(f'## {label}')
        lines.append('')
        for _, file, issue, action in items:
            lines.append(f'- **{file}**')
            lines.append(f'  - Issue: {issue}')
            lines.append(f'  - Action: {action}')
        lines.append('')

    if not findings:
        lines.append('## Clean ✓')
        lines.append('')
        lines.append('No issues found.')

    report_path.write_text('\n'.join(lines), encoding='utf-8')
    return report_path


def append_log(vault, findings, report_path):
    today = datetime.now().strftime('%Y-%m-%d')
    high = sum(1 for f in findings if f[0] == 'high')
    med = sum(1 for f in findings if f[0] == 'medium')
    low = sum(1 for f in findings if f[0] == 'low')
    log_file = vault / '07-wiki' / 'log.md'
    entry = f'\n## [{today}] lint | wiki-lint automated | cron\nFindings: {high} high / {med} medium / {low} low. Report: {report_path.name}\n'
    if log_file.exists():
        with log_file.open('a', encoding='utf-8') as f:
            f.write(entry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fix', action='store_true', help='auto-fix safe violations')
    ap.add_argument('--report', type=str, help='report output path')
    ap.add_argument('--quiet', action='store_true', help='suppress stdout')
    args = ap.parse_args()

    try:
        vault = find_vault()
    except Exception as e:
        print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(2)

    if not args.quiet:
        print(f'Vault: {vault}')

    findings, fixes = check_wiki(vault, fix=args.fix)
    report_path = write_report(vault, findings, fixes, args.report)
    append_log(vault, findings, report_path)

    if not args.quiet:
        high = sum(1 for f in findings if f[0] == 'high')
        med = sum(1 for f in findings if f[0] == 'medium')
        low = sum(1 for f in findings if f[0] == 'low')
        print(f'Findings: {high} high / {med} medium / {low} low')
        print(f'Report: {report_path}')
        if fixes:
            print(f'Auto-fixes: {len(fixes)}')

    if any(f[0] == 'high' for f in findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
