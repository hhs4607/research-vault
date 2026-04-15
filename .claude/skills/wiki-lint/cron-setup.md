---
title: "Cron Setup Guide — Wiki Automation"
date: 2026-04-15
tags: [meta, automation, cron, launchd]
description: "Research Vault 3 automation skills (wiki-lint, ingest, query) 를 cron/launchd 로 자동 실행하는 가이드. Mac + WSL 크로스플랫폼."
---

# Cron Setup — Research Vault Automation

3 Karpathy operations (wiki-lint, ingest, query) 를 스케줄 자동 실행. Mac 과 WSL/Linux 양쪽 지원.

## Vault 경로 환경변수

먼저 `RESEARCH_VAULT` env var 를 설정. 모든 스크립트가 이를 우선 참조.

### Mac (zsh/bash)

`~/.zshrc` 또는 `~/.bashrc`:
```bash
export RESEARCH_VAULT="$HOME/Documents/Research Vault"
# 또는 iCloud 동기화 경로:
# export RESEARCH_VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Research Vault"
```

### WSL

```bash
export RESEARCH_VAULT="/mnt/c/Users/EMDOL/Documents/Research Vault"
```

cron 은 login shell env 를 상속하지 않으므로, cron 엔트리에 `RESEARCH_VAULT=` 를 명시하거나 스크립트가 자체 감지하게 설계됨 (wiki_lint.py 의 `find_vault()` 참조).

---

## Option A: System cron (Mac + Linux 공통)

### Mac crontab

```bash
crontab -e
```

내용:
```cron
# Research Vault automation
# ====================================
RESEARCH_VAULT=/Users/YOUR_USERNAME/Documents/Research Vault
PATH=/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin

# Daily 09:00 — Wiki lint (health check)
0 9 * * * cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --quiet > /tmp/wiki-lint.log 2>&1

# Daily 09:30 — Inbox sweep + auto-ingest (watch mode)
30 9 * * * cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/ingest/ingest.py --watch --auto --quiet > /tmp/ingest.log 2>&1

# Weekly Monday 10:00 — Deep lint + auto-fix safe issues
0 10 * * MON cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --fix --quiet > /tmp/wiki-lint-weekly.log 2>&1
```

### WSL crontab

WSL 은 기본적으로 cron daemon 이 꺼져있음. 시작:
```bash
sudo service cron start
# 또는 영구 설정 (Ubuntu 기준):
sudo systemctl enable cron
```

이후 `crontab -e` 로 같은 방식.

---

## Option B: Mac launchd (권장, Mac-native)

launchd 는 Mac 에서 cron 보다 안정적. 시스템 sleep 후 wake 시에도 missed job 을 실행.

### Step 1: plist 파일 생성

`~/Library/LaunchAgents/com.research-vault.wiki-lint.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.research-vault.wiki-lint</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/Documents/Research Vault/.claude/skills/wiki-lint/wiki_lint.py</string>
        <string>--quiet</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/Documents/Research Vault</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>RESEARCH_VAULT</key>
        <string>/Users/YOUR_USERNAME/Documents/Research Vault</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/wiki-lint.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/wiki-lint.error.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

### Step 2: load + activate

```bash
launchctl load ~/Library/LaunchAgents/com.research-vault.wiki-lint.plist
launchctl list | grep wiki-lint
# 수동 실행 테스트:
launchctl start com.research-vault.wiki-lint
```

### Step 3: 언로드 (중지 시)

```bash
launchctl unload ~/Library/LaunchAgents/com.research-vault.wiki-lint.plist
```

### ingest 용 plist

같은 방식으로 `com.research-vault.ingest.plist` 생성 (Hour=9, Minute=30, arguments 에 `--watch --auto --quiet`).

---

## Option C: Claude Code schedule 스킬 경유

Claude Code CLI 의 `/schedule` 스킬로 setup 가능 (인프라 통합 원할 때):

```
/schedule create wiki-lint "daily 09:00" -- /wiki-lint --quiet
/schedule create ingest-watch "daily 09:30" -- /ingest --watch --auto --quiet
/schedule list
```

→ Remote agent 가 Claude session 을 spawn 해서 실행. 계정 연결 필요.

---

## Paper-review `--auto` mode 지원 추가 필요

현재 `.claude/skills/paper-review/SKILL.md` 는 기본 interactive. Cron 용 auto mode 추가 (2026-04-15 패치 후에도 필요):

```bash
# paper-review --auto 동작: discussion 스킵, metadata + abstract 기반 shallow summary 만 생성
```

추가 패치 예정. 현재는 `/ingest --auto` 가 `paper-review` 로직을 재사용하되 discussion 을 건너뛰도록 구현.

---

## 테스트 체크리스트

Cron 설정 전 수동 테스트:

```bash
# 1. Vault 감지 확인
python3 -c "
import sys; sys.path.insert(0, '$RESEARCH_VAULT/.claude/skills/wiki-lint')
from wiki_lint import find_vault
print(find_vault())
"

# 2. Lint 실행
cd "$RESEARCH_VAULT" && python3 .claude/skills/wiki-lint/wiki_lint.py
# → report 생성 + log append 확인

# 3. Ingest dry-run (watch mode, auto, no-op 시 zero exit)
cd "$RESEARCH_VAULT" && python3 .claude/skills/ingest/ingest.py --watch --auto --dry-run

# 4. Query 수동 테스트 (interactive)
# Claude session 에서: /query "test question"
```

모두 OK 면 cron/launchd 설정 진행.

---

## 로그 모니터링

### 실행 로그

| Skill | Log file (Mac) | Log file (WSL) |
|---|---|---|
| wiki-lint | `/tmp/wiki-lint.log` | `/tmp/wiki-lint.log` |
| ingest | `/tmp/ingest.log` | `/tmp/ingest.log` |
| query (batch) | `07-wiki/query-answers-YYYY-MM-DD.md` | 동일 |

### Vault 로그

모든 작업은 `07-wiki/log.md` 에 실시간 append. 확인:
```bash
tail -30 "$RESEARCH_VAULT/07-wiki/log.md"
```

### Lint 리포트 누적

```bash
ls -la "$RESEARCH_VAULT/07-wiki/lint-report-*.md"
# 주간 정리: 7일 이상 된 리포트 삭제 또는 03-projects 로 이관
```

---

## 알림 (선택)

Lint 에서 high-severity 발견 시 Mac 알림:

```bash
# crontab 엔트리 끝에 덧붙이기
... && osascript -e 'display notification "Wiki lint found issues" with title "Research Vault"' || true
```

exit code 1 (high severity) 일 때 `&&` 건너뛰고 `||` 실행 → notification.

---

## Gotchas

1. **cron PATH**: `/usr/bin/python3` 같은 절대 경로 사용. `python3` 만 쓰면 cron env 에서 못 찾음.
2. **Working dir**: `cd` 필수. 상대 경로 사용 금지 — `WorkingDirectory` 나 `cd "$VAULT"` 로 해결.
3. **Vault sleep/wake**: Mac sleep 중에는 cron 이 miss 함. launchd 는 복구 실행, cron 은 안 함.
4. **iCloud 동기화 지연**: iCloud vault 사용 시 lint 실행 시점에 파일 전체가 local 에 내려와 있는지 확인. `brctl download` 로 force sync 가능.
5. **Zotero 락**: `paper-add` 는 Zotero desktop app 이 꺼져야 DB 쓸 수 있음. Cron ingest 전 `pkill Zotero` 추가 (risky, 사용자 세션 중단 가능 — user 부재 시간만).
6. **Python version**: Mac 기본 `/usr/bin/python3` 은 SIP system Python. pyzotero 등 추가 패키지 필요하면 Homebrew Python 사용: `/opt/homebrew/bin/python3`.
7. **RESEARCH_VAULT 공백 경로**: 경로에 공백 있으면 반드시 따옴표 `"$RESEARCH_VAULT"`.

---

## 권장 스케줄 (초기 설정)

| 시간 | 작업 | Mode |
|---|---|---|
| 매일 09:00 | wiki-lint (quiet) | auto |
| 매일 09:30 | ingest --watch (inbox sweep) | auto |
| 매주 월 10:00 | wiki-lint --fix (deep) | auto |
| 매주 일 18:00 | query batch (weekly synthesis refresh) | batch |
| (on-demand) | /ingest DOI / /query question | interactive |

---

## 관련 파일

- `.claude/skills/wiki-lint/SKILL.md` + `wiki_lint.py`
- `.claude/skills/ingest/SKILL.md`
- `.claude/skills/query/SKILL.md`
- `07-wiki/_protocol.md` — wiki 규칙
- `08-raw/_protocol.md` — raw 규칙
- `CLAUDE.md` — vault schema
