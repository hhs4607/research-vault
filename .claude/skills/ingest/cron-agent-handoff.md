---
title: "Ingest — Cron Agent Handoff"
date: 2026-04-15
tags: [meta, automation, cron, handoff, ingest]
description: "크론잡 에이전트(예: Mac Claude)에게 /ingest 스킬 자동 실행을 지시할 때 복붙 전달할 인수용 구조. user 는 이 문서만 공유하면 됨."
---

# Ingest — Cron Agent Handoff

이 문서는 **user 가 크론잡 에이전트에게 복붙 전달**하는 instruction 구조다. 에이전트는 이 문서 + `.claude/skills/ingest/SKILL.md` + `cron-setup.md` 를 읽고 설정 + 실행할 수 있어야 한다.

---

## Part 1 — 에이전트에게 전달할 지시문 (복사·붙여넣기용)

```
Research Vault 의 /ingest 스킬을 cron 으로 자동 실행 세팅해줘.

볼트 위치:
- Mac: ~/Documents/Research Vault  (또는 iCloud 동기 경로)
- Env var: export RESEARCH_VAULT="<path>" 를 ~/.zshrc 에 추가

스킬 파일:
- .claude/skills/ingest/SKILL.md   — 전체 설계·schema·workflow
- .claude/skills/ingest/ingest.py  — 실행체 (Python 3.8+, 외부 패키지 불필요)
- .claude/skills/ingest/cron-agent-handoff.md — 이 문서 (자기 자신)

수행할 작업:

1. 환경 확인
   - which python3 (3.8+ 확인)
   - cd "$RESEARCH_VAULT" && python3 .claude/skills/ingest/ingest.py --help
   - 정상 실행 확인

2. 테스트 (shallow mode 단일 DOI)
   python3 .claude/skills/ingest/ingest.py \
       10.1016/j.ijfatigue.2008.07.002 \
       --mode shallow \
       --agent cron

   확인:
   - 07-wiki/paper-notes/Post2008.md 생성 (또는 기존 paper 경우 새 suffix)
   - 07-wiki/index.md 에 ## Paper-notes 섹션에 entry 추가
   - 07-wiki/log.md 에 ## [YYYY-MM-DD] ingest 엔트리 append
   - 생성된 paper-note frontmatter 에 ingest_agent: "cron", ingest_mode: "shallow"

3. Paper-1 mode 테스트
   python3 .claude/skills/ingest/ingest.py \
       10.1177/002199837300700404 \
       --mode paper1 \
       --section '§2.1' \
       --tier A \
       --role anchor \
       --tier-reason "peer-reviewed, J Composite Materials" \
       --agent cron

   확인:
   - 07-wiki/paper-notes/HashinRotem1973.md (또는 유사) — frontmatter 에 paper1_* 필드 완전
   - 03-projects/Paper-1/references/_pending.md 에 DRAFT/CLAIMED row append
   - 03-projects/Paper-1/references/refs-log.md 에 ADD entry append

4. Watch mode 스케줄
   01-inbox/ 에 드롭된 PDF 를 자동 ingest (shallow mode) 하는 daily sweep.

   crontab 권장:
   0 9 * * * cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/ingest/ingest.py --watch --mode shallow --auto --agent cron --quiet > /tmp/ingest.log 2>&1

   또는 launchd plist (Mac 권장) — cron-setup.md 참조.

5. Wiki-lint + ingest 통합 스케줄
   .claude/skills/wiki-lint/cron-setup.md 의 권장 schedule 따라:
   - 매일 09:00 — wiki-lint
   - 매일 09:30 — ingest --watch
   - 매주 월 10:00 — wiki-lint --fix
   - 매주 일 18:00 — query batch (선택)

6. 완료 후 report
   - crontab -l 결과 공유
   - /tmp/ingest.log 첫 실행 확인
   - 07-wiki/log.md 최근 10 줄 tail

주의:
- paper-add 는 Zotero desktop 닫혀있어야. 현재 ingest.py 는 Zotero 등록 미포함 (raw 저장만). 완전 통합은 paper-add.py 호출 체인 필요 — 추후 Phase 2.
- --watch mode 는 현재 placeholder (PDF metadata 추출 미구현). 초기는 DOI 기반 단일 실행만 안정적.
- Python 3.8+ 필요. Mac 기본 /usr/bin/python3 은 3.9+.
```

---

## Part 2 — 스킬 기능 요약 (에이전트가 읽어야 할 핵심)

### 3 modes

| Mode | 용도 | Body depth | Paper-1 fields | Cron-friendly |
|---|---|---|---|---|
| `shallow` | 대량 harvest / inbox sweep | abstract + 1-line | 없음 | ✓ |
| `deep` | 일반 paper 리뷰 | 연구배경/주장/method/limit | 없음 | 부분 |
| `paper1` | Paper-1 reference | deep + Paper-1 블록 | 완전 | 부분 |

### Paper-1 mode 필수 인자

- `--section §N.M` — 현재 numbering (§1/§2/§3/§4/§5)
- `--tier A|B|C|D|E` — evidence tier
- `--role anchor|bridge|context|hedge|self-cite|open-slot`
- (권장) `--tier-reason "..."` — reviewer defensibility 한 줄
- §4 papers: `--dt-classification DT|SHM-only|not-DT` (Def-Moderate)
- Tier D: `--tier-d-mode body-count|footnote|context` (H-Moderate)
- 특수: `--wording-constraint L-1|canonical|none`

### 3개 인자 (`--section --tier --role`) 모두 주면 `paper1_status: CONFIRMED`. 하나라도 빠지면 `CANDIDATE` 로 저장되고 user review 대기.

### Paper-note 저장 위치 + 자동 업데이트 대상

```
08-raw/papers/{AuthorYear}.pdf              — PDF 원본 (paper-add 체인 — 현재 ingest.py 는 생략)
07-wiki/paper-notes/{AuthorYear}.md         — 생성 (mode 별 depth)
07-wiki/index.md                             — ## Paper-notes 섹션에 entry
07-wiki/log.md                               — ## [YYYY-MM-DD] ingest entry

Paper-1 mode only:
03-projects/Paper-1/references/_pending.md   — DRAFT/CLAIMED row
03-projects/Paper-1/references/refs-log.md   — ADD entry
```

### Cron 권장 스케줄

```cron
# 매일 09:00 — wiki-lint
0 9 * * * cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --quiet

# 매일 09:30 — ingest inbox sweep (현재는 placeholder, PDF 감지만)
30 9 * * * cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/ingest/ingest.py --watch --auto --quiet --agent cron

# 매주 월 10:00 — wiki-lint --fix
0 10 * * MON cd "$RESEARCH_VAULT" && /usr/bin/python3 .claude/skills/wiki-lint/wiki_lint.py --fix --quiet
```

### Exit codes

- 0 = 성공
- 1 = 일부 실패 (wiki-lint high-severity 등)
- 2 = 실행 에러 (vault 미감지 / DOI 실패 등)

---

## Part 3 — 알려진 한계 (Phase 2 TODO)

1. **PDF download 미통합**: 현재 `ingest.py` 는 paper-note 생성·wiki 업데이트만. 원본 PDF 확보는 수동 또는 `/paper-add` 별도 실행 필요. Phase 2 에서 paper-add.py 호출 체인 예정.

2. **URL mode 미구현**: 현재 DOI 만 지원. arXiv / ScienceDirect URL 등은 WebFetch + parser 추가 필요.

3. **Watch mode 는 placeholder**: `01-inbox/*.pdf` 개수만 report, 실제 자동 ingest 는 PDF metadata 추출 구현 필요 (PyPDF2 or pdfplumber).

4. **Cross-reference 자동화 제한**: SKILL.md 에 Step 5 (entity/concept/synthesis update) 로직 문서화됐으나 `ingest.py` 에는 미구현. Phase 2.

5. **Def-Moderate heuristic 미구현**: `--dt-classification` 인자로 수동 지정. 자동 감지는 paper text 읽고 keyword 기반 판단 필요.

6. **Zotero 등록 미포함**: `paper-add` 는 별도 호출. 통합은 Phase 2.

---

## Part 4 — 에이전트 질문 대응

에이전트가 다음 질문하면 이렇게 응답:

**Q: paper1 mode 인데 section 뭘 줘야 해?**
→ `03-projects/Paper-1/references/` 의 `ch-N-*/refs.md` 참조. 없으면 user 에 확인.

**Q: Tier 판정 모호.**
→ `03-projects/Paper-1/references/tier-system.md` 로 판정. 모호하면 `CANDIDATE` 로 저장 + `_pending.md` 에 기록, user review 대기.

**Q: Watch mode 자동 ingest 구현 요청.**
→ Phase 2 TODO. 현재는 inbox sweep 은 placeholder. PDF metadata 추출 구현 시점은 user 가 지정.

**Q: 실행 실패 + 에러.**
→ vault 감지 실패면 `RESEARCH_VAULT` env 확인. Crossref 실패면 DOI 오타 확인. 그 외는 `/tmp/ingest.log` stderr 전달.

**Q: Paper-note 이미 존재 (충돌).**
→ `AuthorYearb`, `AuthorYearc` suffix 로 자동 생성. 동일 DOI 인 경우 `--force` 필요.

---

## Part 5 — Vault 규칙 re-read 의무

에이전트는 세션 시작 시 다음 문서를 **강제 로드**:

1. `CLAUDE.md` — Vault schema
2. `07-wiki/_protocol.md` — wiki 운영 규칙
3. `08-raw/_protocol.md` — raw immutability
4. `03-projects/Paper-1/references/PROTOCOL.md` — Paper-1 multi-agent rules (paper1 mode 시)
5. `.claude/skills/ingest/SKILL.md` — 이 스킬 상세

---

## Part 6 — 기대 산출물 체크리스트 (cron 에이전트 첫 세션 완료 시)

- [ ] `~/.zshrc` 에 `RESEARCH_VAULT` env var 설정
- [ ] `python3 .claude/skills/ingest/ingest.py --help` 정상 출력
- [ ] shallow mode 테스트 성공 (paper-note + index + log 생성 확인)
- [ ] paper1 mode 테스트 성공 (+ _pending + refs-log 업데이트 확인)
- [ ] crontab (또는 launchd) 등록 완료
- [ ] 첫 cron 실행 log 확인 (/tmp/ingest.log 또는 07-wiki/log.md)
- [ ] Phase 2 TODO 리스트 user 에게 보고

---

## Part 7 — Script API (Python 에이전트가 프로그래밍적으로 호출할 때)

`ingest.py` 는 CLI entry + module 양쪽 지원:

```python
from pathlib import Path
import sys
sys.path.insert(0, '<vault>/.claude/skills/ingest')
from ingest import find_vault, fetch_crossref, generate_paper_note, resolve_author_year

vault = find_vault()
meta = fetch_crossref('10.xxxx/...')
# ... 직접 호출 가능
```

주요 함수:
- `find_vault() -> Path`
- `fetch_crossref(doi: str) -> dict`
- `derive_author_year(meta: dict) -> str`
- `resolve_author_year(vault: Path, base: str) -> (str, bool)`  — suffix 처리
- `generate_paper_note(meta, mode, vault, args, author_year) -> str`  — markdown 반환
- `append_index(vault, author_year, description)`
- `append_log(vault, author_year, mode, agent, extras='')`
- `append_paper1_pending(vault, author_year, doi, args)` — paper1 전용
- `append_paper1_refs_log(vault, author_year, args)` — paper1 전용

---

## 관련 파일

- [[SKILL.md|SKILL.md]] — 설계 상세
- [[ingest.py|ingest.py]] — 실행체
- `.claude/skills/wiki-lint/cron-setup.md` — cron/launchd 공통 가이드
- `.claude/skills/wiki-lint/wiki_lint.py` — health check 실행체
- `03-projects/Paper-1/references/PROTOCOL.md` — Paper-1 multi-agent
