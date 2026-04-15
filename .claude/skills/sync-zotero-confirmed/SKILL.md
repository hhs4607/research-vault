---
name: sync-zotero-confirmed
description: "Sync CONFIRMED paper-notes (paper1_status=CONFIRMED) to Zotero library + chapter collection. Separated from /ingest per Paper-1 PROTOCOL. Cron-friendly confirm-time sync only."
argument-hint: "[--apply] [--pattern §N.M] [--attach-pdf] [--dry-run]"
---

# Sync Zotero Confirmed — Confirm-time Zotero Integration

`/ingest` 와 분리된 별도 skill. Paper-1 PROTOCOL 준수: **CONFIRMED 상태 + slot 확정된 paper-notes 만** Zotero 에 동기화.

## Why separate?

Per Paper-1 `references/PROTOCOL.md` §8 (Zotero 등록 정책):
- 자동 DOI import 금지 (metadata 정확성 의심 과거 경험)
- **CONFIRMED 된 refs 만 수동 검증 후 등록**

`/ingest` 가 ingest-time Zotero 등록 하면 DRAFT/CANDIDATE status 인데도 library 오염. 이 skill 은 confirm 상태만 filter.

## Usage

```bash
# Dry-run (read-only, what would be synced)
/sync-zotero-confirmed
/sync-zotero-confirmed --pattern '§4.*'

# Actual sync
/sync-zotero-confirmed --apply
/sync-zotero-confirmed --apply --pattern '§2.*'
/sync-zotero-confirmed --apply --attach-pdf   # PDF attachment 도 (기본 off)
```

## Input criteria (필터)

`07-wiki/paper-notes/*.md` 중 다음 **모두** 만족:
- `type: paper-note` frontmatter
- `paper1_status: CONFIRMED`
- `paper1_sections` 최소 1개
- `paper1_slots` 최소 1개 (단락 수준)
- `paper1_tier` ∈ A/B/C/D/E
- `doi` 있음
- (optional) `--pattern §4.*` 필터: `paper1_sections` 가 pattern 매칭

## Workflow

```
1. Scan 07-wiki/paper-notes/ → CONFIRMED + slot 확정된 것 추출
2. For each:
   a. Zotero find_by_doi(doi)
      - 있으면 → item_key 재사용
      - 없으면 → Crossref fetch → create_item → item_key 획득
   b. assign_to_chapter(item_key, paper1_sections) — addto_collection() 사용
      - SHARED (paper1_shared_sections) 있으면 multi-collection
   c. (optional, --attach-pdf) PDF 있으면 attach
   d. paper-note frontmatter 에 zotero_key 기록 + date_updated 갱신
3. 07-wiki/log.md append: [YYYY-MM-DD] zotero-sync | N papers | agent
```

## Chapter collection mapping (Paper-1)

```python
CHAPTER_COLLECTIONS = {
    '§1': 'ICDZS7UB',  # Ch.1 Introduction
    '§2': 'CKMC5AWI',  # Ch.2 Classical Methods
    '§3': '726X7VBU',  # Ch.3 AI-Enhanced
    '§4': 'CB59XCM8',  # Ch.4 Digital Twin
    '§5': 'A5D2JZD4',  # Ch.5 Synthesis Roadmap
}
```

Env override: `ZOTERO_CH_1_KEY` 등으로 개별 재정의 가능 (Codex B5 권장).

## API correctness (Codex 반영)

| 행동 | Wrong (v1 plan) | Right (v2) |
|---|---|---|
| Rate limit | `time.sleep(0.3)` fixed | **pyzotero 자체 backoff 위임** |
| Collection 할당 | `update_item(item, data)` full-mutate | **`addto_collection(coll_key, item)`** |
| Error handling | broad `except: pass` | specific HTTPError / KeyError 핸들링 |
| PDF attachment | 기본 on | **기본 off, `--attach-pdf` 명시 필요** (Zotero storage 거의 full) |

## Dry-run report

```
=== sync-zotero-confirmed dry-run ===
Vault: /Users/.../Research Vault
Pattern: all

Scanning 07-wiki/paper-notes/...
  214 paper-notes total
    → 42 CONFIRMED + slot
    → 12 already have zotero_key (would update collection only)
    → 30 would create new Zotero item

Estimated operations:
  - Zotero API calls: 30 create + 42 collection assign = 72
  - Time estimate: ~3 minutes (pyzotero rate limit)

Action required: --apply to execute.
```

## Cron

### 매일 22:00 (권장)
```cron
0 22 * * * cd "$RESEARCH_VAULT" && ~/.venvs/research-vault/bin/python \
    .claude/skills/sync-zotero-confirmed/sync.py --apply --quiet \
    > /tmp/zotero-sync.log 2>&1
```

### launchd plist
```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>source ~/.config/research-vault.env && cd "$RESEARCH_VAULT" && ~/.venvs/research-vault/bin/python .claude/skills/sync-zotero-confirmed/sync.py --apply --quiet</string>
</array>
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key><integer>22</integer>
    <key>Minute</key><integer>0</integer>
</dict>
```

## Env vars

```bash
ZOTERO_USER_ID=14865742
ZOTERO_API_KEY=<secret>
# Optional overrides
ZOTERO_CH_1_KEY=custom-key-1   # etc.
```

## Exit codes

- 0: success (all CONFIRMED synced)
- 1: partial success (some failed)
- 2: execution error (env missing, vault not found)

## Output

- stdout: summary (unless `--quiet`)
- `07-wiki/log.md`: append entry
- Per-paper frontmatter: `zotero_key`, `date_updated` update

## Failure modes

| Fault | Behavior |
|---|---|
| Zotero API down | retry 3x with backoff, then skip paper + log warning |
| DOI Crossref fail | skip paper, log |
| paper-note frontmatter 파싱 실패 | skip, log |
| Chapter key invalid | log warning, skip chapter assign (item still created) |
| Attachment failure (PDF corrupt) | item created, attachment skipped, log |

## 관련 파일

- `sync.py` — 실행체
- `tests/test_sync.py` — unit tests
- `03-projects/Paper-1/references/PROTOCOL.md` §8 Zotero 정책
- `03-projects/Paper-1/references/tier-system.md`
- `.claude/skills/ingest/` — Phase 2 core (이 skill 은 별도)

## Handoff to cron agent

Mac Claude 에게 넘길 때:
```
Research Vault 에 sync-zotero-confirmed 스킬 있음.
.claude/skills/sync-zotero-confirmed/SKILL.md 읽고 매일 22:00 cron/launchd 등록.
pyzotero + RESEARCH_VAULT + ZOTERO_USER_ID + ZOTERO_API_KEY 필요.
첫 실행은 --dry-run 으로 검증 후 --apply.
```
