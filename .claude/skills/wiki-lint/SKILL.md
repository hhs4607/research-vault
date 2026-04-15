---
name: wiki-lint
description: "Wiki health check — orphan pages, broken wikilinks, frontmatter compliance, naming violations, index/log consistency. Cron-ready non-interactive."
argument-hint: "[--fix] [--report path] [--quiet]"
---

# Wiki Lint — Health Check for 07-wiki/

Run periodic health checks on `07-wiki/` per Karpathy LLM Wiki pattern. Identifies orphan pages, broken cross-references, frontmatter violations, naming issues. **Non-interactive by default** — cron-safe.

**Input** (all optional):
- `--fix` : attempt auto-fixes for safe violations (missing `type:` etc.)
- `--report path` : write report to specific path (default: `07-wiki/lint-report-YYYY-MM-DD.md`)
- `--quiet` : no stdout, only file output + log append

## Cross-platform vault detection

```python
# wiki_lint.py의 vault 감지 로직
import os
from pathlib import Path

def find_vault():
    # 1. env var
    if v := os.environ.get('RESEARCH_VAULT'):
        return Path(v)
    # 2. cwd 및 부모 순회하며 CLAUDE.md + 07-wiki 쌍 찾기
    p = Path.cwd()
    for parent in [p, *p.parents]:
        if (parent / 'CLAUDE.md').exists() and (parent / '07-wiki').is_dir():
            return parent
    # 3. platform-specific 기본값
    import platform
    if platform.system() == 'Darwin':
        candidates = [Path.home() / 'Documents/Research Vault',
                     Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Research Vault']
    else:  # WSL/Linux
        candidates = [Path('/mnt/c/Users/EMDOL/Documents/Research Vault')]
    for c in candidates:
        if c.exists() and (c / 'CLAUDE.md').exists():
            return c
    raise RuntimeError("Research Vault not found. Set RESEARCH_VAULT env var.")
```

## Workflow

### Step 1: Detect vault
```bash
python3 "<vault>/.claude/skills/wiki-lint/wiki_lint.py" [--fix] [--report PATH] [--quiet]
```

스크립트가 자동 vault 감지 (env var → cwd 순회 → platform default).

### Step 2: Run checks (script 내부)

| Check | 조건 | Severity |
|---|---|---|
| **Frontmatter: `type:` 누락** | `07-wiki/**/*.md` 중 paper-notes/_broken 제외 | High |
| **Broken wikilink** | `[[target]]` 이 어느 파일 basename 과도 매칭 안 됨 | High |
| **Orphan page** | 0 inbound wikilink (paper-notes 제외 — 개별 paper 는 synthesis 에서 선택적 link) | Medium |
| **Paper-note naming violation** | `07-wiki/paper-notes/*.md` 중 `AuthorYear[a-z]?\.md` 패턴 밖 (제외: `_broken/`) | Medium |
| **Index.md 누락** | 실제 존재 wiki 페이지가 `07-wiki/index.md` 에 entry 없음 | Low |
| **08-raw 위반** | `08-raw/` 에 paper-notes 또는 해석-성 md 발견 (허용: `_protocol.md`, `MOC.md`, subfolder/*.pdf, draft-lineage/*.md) | High |
| **Log last entry stale** | `07-wiki/log.md` 마지막 entry 가 30 일 이상 | Low |

### Step 3: Report 작성

Output: Markdown report with:
- Summary (counts per severity)
- Detailed findings (file path + issue)
- Suggested actions
- `--fix` mode 에서 자동 적용된 변경 list

Report 파일명: `07-wiki/lint-report-YYYY-MM-DD.md` (또는 `--report PATH` 지정)

### Step 4: Log append

`07-wiki/log.md` 에 자동 append:
```markdown
## [YYYY-MM-DD] lint | wiki-lint automated | cron
Findings: N high / M medium / K low. Report: lint-report-YYYY-MM-DD.md
```

### Step 5: Exit code

- 0 : no high-severity issues
- 1 : high-severity issues found (for cron alerting)
- 2 : execution error

## Auto-fix (--fix mode)

안전한 자동 수정:
- frontmatter `type:` 누락 → folder 기반 기본값 (`paper-notes/` → `type: paper-note`, `entities/` → `type: entity`, etc.)
- `date_created` / `date_updated` 누락 → 파일 stat mtime
- Paper-note naming: `Author Year.md` → `AuthorYear.md` (공백 제거) — **dangerous, off by default, only suggest**

위험한 수정은 수행하지 않음:
- Orphan page 삭제 (X)
- Broken wikilink auto-resolve (X) — 사용자 확인 필요
- _broken/ 파일 재명명 (X)

## Cron 실행 예시

### WSL/Linux crontab:
```bash
# 매일 오전 9시 wiki-lint 실행 (quiet, report file only)
0 9 * * * cd "/mnt/c/Users/EMDOL/Documents/Research Vault" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --quiet
```

### Mac crontab:
```bash
0 9 * * * cd "$HOME/Documents/Research Vault" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --quiet
```

### Mac launchd (권장):
`~/Library/LaunchAgents/com.research-vault.wiki-lint.plist` 생성. 가이드는 `wiki-lint/cron-setup.md` 참조.

### Claude Code schedule 스킬 경유:
```
/schedule create wiki-lint daily 09:00 -- /wiki-lint --quiet
```

## Non-interactive 원칙

- stdout/stderr: `--quiet` 시 zero output (cron-friendly)
- File I/O: report + log append 만
- User prompt: 없음
- Network: 없음 (순수 filesystem)
- Exit code: alerting 용

## 관련 파일

- `wiki_lint.py` — 실행 스크립트
- `cron-setup.md` — Mac/WSL cron 설정 가이드
- [[../../07-wiki/_protocol]] — 규칙 원본
- [[../../07-wiki/log]] — lint 결과 append 대상
