---
name: ingest
description: "Paper ingest with Paper-1-aware schema. 3 modes (shallow/deep/paper1). Saves to 08-raw/papers/ + 07-wiki/paper-notes/, updates entity/concept/synthesis + index + log. Cron-ready."
argument-hint: "[DOI|URL|PDF] [--mode shallow|deep|paper1] [--section §N.M] [--tier A|B|C|D|E] [--role anchor|bridge|context|hedge] [--watch]"
---

# Ingest — Paper-aware Karpathy LLM Wiki Op #1

Single entry point to ingest a paper into the vault with the right level of interpretation. **Paper-1 mode** produces notes directly usable in drafting (with Tier + slot + Def-Moderate + L-1 fields); **shallow** mode for bulk harvest; **deep** mode for thorough review.

## Usage

```
/ingest <source> [options]
/ingest 10.1016/j.ijfatigue.2008.07.002 --mode paper1 --section §2.1 --tier A --role anchor
/ingest https://arxiv.org/abs/2403.xxxxx --mode deep
/ingest /path/to/paper.pdf --mode shallow
/ingest --watch --auto                  # inbox sweep, cron-friendly
```

## Modes (핵심 설계)

| Mode | When | Body depth | Paper-1 schema | Cron-safe |
|---|---|---|---|---|
| `shallow` | 대량 harvest (master list 등) | abstract + 1-line method/contribution | 최소 (citation_key, doi, authors) | ✓ |
| `deep` | 일반 리뷰 (Paper-1 외) | full structured analysis | 없음 | 부분 (user 토론 없이) |
| `paper1` | Paper-1 references 용 | deep + Paper-1 classification 블록 필수 | 완전 | 부분 — tier/section 인자 없으면 CANDIDATE |
| `watch` | `01-inbox/` sweep | mode per-file (PDF filename 힌트) | auto-detect | ✓ |

**기본값**: `shallow`. Paper-1 drafting 에 쓸 refs 는 `--mode paper1 --section ... --tier ...` 명시 강제.

## Output Schema (Paper-1 Mode)

`07-wiki/paper-notes/{AuthorYear}.md` 생성 시 **정확히 이 template** 준수:

```markdown
---
# =========================
# 1. Bibliographic (stable, Crossref)
# =========================
type: paper-note
citation_key: AuthorYear
doi: "10.xxxx/..."
title: "..."
authors: "First Author et al."
year: YYYY
journal: "..."
volume: "..."
pages: "..."
aliases: ["Author Year", "..."]

# =========================
# 2. Asset tracking
# =========================
pdf_path: "08-raw/papers/AuthorYear.pdf"
pdf_available: true
oa_status: open | closed | preprint
ingest_date: 2026-04-15
ingest_agent: §N-agent | user | cron
ingest_mode: shallow | deep | paper1

# =========================
# 3. Paper-1 classification (paper1 mode REQUIRED)
# =========================
paper1_sections: ["§N.M"]               # 현 numbering (§1 Intro / §2 Classical / §3 AI / §4 DT / §5 Synthesis)
paper1_slots: ["§N.M P_k"]              # 단락 단위, 확정 시
paper1_tier: A | B | C | D | E          # Tier 시스템 (references/tier-system.md)
paper1_role: anchor | bridge | context | hedge | self-cite | open-slot
paper1_status: DRAFT | CANDIDATE | CONFIRMED | SHARED | SUPERSEDED
paper1_shared_sections: []              # 다중 섹션 사용 (SHARED 시)

# =========================
# 4. §4-specific (§4 papers only)
# =========================
dt_classification: DT | SHM-only | not-DT     # D2 Def-Moderate
tier_d_mode: body-count | footnote | context  # D4 H-Moderate (Tier D only)
wording_constraint: L-1 | canonical | none    # D3 L-1 wording discipline

# =========================
# 5. Standard wiki
# =========================
tags: [paper-1/section-N, tier-X, research/...]
date_created: 2026-04-15
date_updated: 2026-04-15
description: "한 줄 Korean 요약 (index.md 재활용)"
source: "DOI URL"
zotero_key: "..."
---

# {Full Title}

## 논문 정보
- **Journal / Venue**: ...
- **DOI**: ...
- **Open access**: ...
- **소속**: ...
- **PDF**: `08-raw/papers/{AuthorYear}.pdf` (size, pages)

## Abstract
(verbatim, journal/preprint abstract)

## 연구 배경
(paper 가 어떤 context 에서 나왔나 — 2-4 문장)

## 핵심 주장 / 기여
1. ...
2. ...
3. ...

## Method
(기술적 접근 요약)

## Verbatim Quotes (중요 명제만)
> "canonical definition or L-1 content..." — p.N
> (only include if wording_constraint = L-1 or canonical)

## Paper-1 Usage
### §N.M P_k (해당 섹션/단락)
- **Claim**: paper 의 어떤 주장을 Paper-1 N.M P_k 에 쓰는가
- **Tier**: A (근거: peer-reviewed venue / 저자 신뢰도 / 외부 검증)
- **Wording discipline**: L-1 (Lillgrund 등) 또는 standard
- **Hedging**: none / Tier D body-count / Tier D footnote

(multiple slots if SHARED)

## Tier 근거
(왜 A/B/C/D/E 인가, reviewer defensibility 한 문단)

## DT Classification (§4 papers only)
- **Def-Moderate 적용**: DT (virtual model + sensor-driven state update 확인) / SHM-only (feedback loop 없음 → §4.2 로 분류) / not-DT
- **근거**: 논문 본문의 어느 부분에서 이 분류를 정당화하는가

## H-Moderate (§4 Tier D only)
- **Body count**: verifiable claim (예: "Vestas AOM covers 18,000+ turbines")
- **Footnote metric**: performance metric (예: "75% cost reduction")
- (Tier D 아니면 섹션 생략)

## Limitations
- (paper 자체 acknowledged limitations)
- (Paper-1 관점 한계 — 이 paper 가 Paper-1 에서 못 하는 것)

## Cross-references
- **Entities**: [[Org1]], [[Author]], [[Standard]]
- **Concepts**: [[Method A]], [[Framework B]]
- **Syntheses**: [[Landscape Page]]
- **Related papers**: [[AuthorYear1]], [[AuthorYear2]]

## Ingest audit
- {YYYY-MM-DD} ingest {agent-id} --mode paper1 --section §N.M --tier X --role Y
- (이후 변경 append)
```

## Workflow (paper1 mode 기준)

### Step 1: Parse input + mode

```python
source = parse_source(args.source)       # DOI / URL / PDF
mode = args.mode                          # shallow/deep/paper1
section = args.section                    # §2.1, §4.3, ...
tier = args.tier                          # A/B/C/D/E
role = args.role                          # anchor/bridge/...
```

### Step 2: Metadata fetch → AuthorYear

- DOI → Crossref API `https://api.crossref.org/works/{DOI}` → authors, year, title, journal
- URL → WebFetch + parse (arXiv / ScienceDirect / IEEE / Wiley 별 selector)
- PDF → filename pattern 매칭, Zotero search, 또는 첫 페이지 extract

**AuthorYear 규칙**:
- `{FirstAuthorLastName}{Year}` (예: `Hao2025`)
- 충돌 시 suffix: `AuthorYearb`, `AuthorYearc`, ...
- 중복 체크: `07-wiki/paper-notes/{AuthorYear}.md` 있으면 update 모드로 전환

### Step 3: Raw 저장

```
1. 08-raw/papers/{AuthorYear}.pdf 존재 체크
2. PDF 확보 (paper-add 로직):
   - Unpaywall API (open access)
   - Crossref link-set (publisher direct)
   - Google Scholar / ResearchGate crawl (fallback)
3. 성공 시: cp {downloaded}.pdf 08-raw/papers/{AuthorYear}.pdf
4. 실패 시: pdf_available: false, 메타데이터만으로 진행
```

### Step 4: Paper-note 생성 (mode 별)

**shallow mode**:
- Abstract (Crossref 있으면) + 1-line method/contribution
- Paper-1 섹션 블록 생략

**deep mode**:
- PDF 전체 read (가능한 경우)
- 연구 배경 / 핵심 주장 / Method / Limitations 문단 작성
- Paper-1 섹션 블록 **없음** (일반 리뷰용)

**paper1 mode**:
- Deep mode 전체 +
- Frontmatter: paper1_* 필드 강제 작성 (인자 기반)
- Body: `## Paper-1 Usage` 섹션 필수
- Body: `## Tier 근거` 필수
- `--section §4.*` 일 때: `## DT Classification` 섹션 필수 (Def-Moderate heuristic)
- `--tier D` 일 때: `## H-Moderate` 섹션 필수
- `--wording-constraint L-1` 일 때: `## Verbatim Quotes` 에 해당 문장 추출 필수

### Step 5: Cross-cutting wiki 업데이트

paper-note 저장 후 **반드시**:

**5-a. Entity**:
- Paper 저자 / 기관 / 언급된 standard / tool / dataset 식별
- 각각:
  - `ls 07-wiki/entities/{Name}.md` 있으면 → 해당 파일에 "## Mentioned in" 섹션에 `[[AuthorYear]]` append
  - 없으면 → 신규 entity 파일 생성 (basic frontmatter + 한 줄 요약 + `sources: [AuthorYear]`)

**5-b. Concept**:
- Paper 가 도입/사용한 method / algorithm / framework 명시
- 기존 concept 있으면 → update (sources 리스트에 AuthorYear 추가)
- 없으면 → `_pending-concepts.md` 에 기록 (user 승인 대기; 자동 생성 금지)

**5-c. Synthesis**:
- `07-wiki/syntheses/` 전체 grep
- 이 paper 가 fit 하는 synthesis 식별 → 해당 페이지 적절 섹션에 `[[AuthorYear]]` insert
- 복수 synthesis fit 가능

**5-d. Comparison**: (optional, 해당 시)
- 기존 comparison 에 포함될 수 있으면 row 업데이트

### Step 6: Index + Log 업데이트

`07-wiki/index.md`:
```markdown
## Paper-notes
- [[AuthorYear]] — {description from frontmatter}
```
(이미 entry 있으면 description 갱신)

`07-wiki/log.md`:
```markdown
## [YYYY-MM-DD] ingest | AuthorYear | {agent-id}
Mode: paper1. Section: §N.M. Tier: X. Role: Y. Updated: {entity-list}. PDF: {available|n/a}.
```

### Step 7: Paper-1 PROTOCOL 반영 (paper1 mode)

- `03-projects/Paper-1/references/_pending.md` 에 DRAFT 엔트리 추가 (status=DRAFT 또는 CANDIDATE)
- `03-projects/Paper-1/references/refs-log.md` 에 `ADD` 엔트리 append
- `--role CONFIRMED` 인자 있으면 해당 `ch-N-*/refs.md` spine 에 직접 entry 추가

### Step 8: Zotero 등록 (선택)

- `paper-add` 스킬 사용 (Zotero desktop 닫혀야 함)
- 성공 시 해당 chapter collection 에 할당 (Paper-1 classification 기반)

## Cron Usage

### Daily inbox sweep (권장):
```bash
0 9 * * * cd "$RESEARCH_VAULT" && python3 .claude/skills/ingest/ingest.py --watch --mode shallow --auto --quiet
```

### Paper-1 drafting 세션 (on-demand):
```bash
# Claude Code session 에서:
/ingest 10.1016/... --mode paper1 --section §4.3 --tier A --role anchor
```

### Reprocess (shallow → deep/paper1 승격):
```bash
/ingest AuthorYear --reprocess --mode paper1 --section ...
```

## 실패 처리

- PDF 다운로드 실패 → note 만 생성, `pdf_available: false`
- Crossref metadata 없음 → `--manual-author "Kim" --manual-year 2024` 요청
- `--auto` 에서 ambiguous → `_pending-ingest.md` 에 기록, continue
- Paper-1 필수 인자 (`--section --tier --role`) 누락 시 paper1 mode → CANDIDATE status 로 저장, user review 대기

## Python 실행체

`.claude/skills/ingest/ingest.py` — SKILL.md 의 로직을 실제 실행하는 Python wrapper.

주요 함수:
- `find_vault()` — 크로스플랫폼 vault 감지
- `fetch_crossref(doi)` — Crossref API 조회
- `parse_pdf(path)` — PyPDF 로 첫 페이지 메타데이터 추출
- `generate_paper_note(metadata, mode, paper1_args)` — 스키마 준수 파일 생성
- `update_wiki_pages(author_year, ...)` — entity/concept/synthesis/index/log 업데이트
- `main()` — CLI entry point, mode switch

## 관련 파일

- `.claude/skills/ingest/ingest.py` — 실행체
- `.claude/skills/ingest/templates/` — mode 별 template
- `.claude/skills/paper-add/` — PDF + Zotero
- `.claude/skills/paper-review/` — deep mode 때 body 작성에 활용
- `07-wiki/_protocol.md` — wiki 규칙
- `08-raw/_protocol.md` — raw 규칙
- `03-projects/Paper-1/references/PROTOCOL.md` — Paper-1 multi-agent rules
- `03-projects/Paper-1/references/tier-system.md` — Tier A-E

## Cron Agent Handoff

이 스킬을 크론잡 에이전트에게 실행 지시할 때 전달할 구조는
[[cron-agent-handoff]] 참조 (`cron-agent-handoff.md` 파일).
