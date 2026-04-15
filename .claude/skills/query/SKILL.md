---
name: query
description: "Karpathy LLM Wiki Query operation — search wiki first, synthesize answer with citations, optionally promote valuable answers to new wiki pages. Compounding knowledge."
argument-hint: "[question] [--promote] [--depth N] [--scope wiki|all]"
---

# Query — Wiki-First Search + Cited Synthesis (Karpathy LLM Wiki Op #2)

Answer a knowledge question by searching the wiki first. Return citations to wiki pages and paper-notes. Offer to promote reusable answers to new wiki pages.

**Input**:
- `question` : 자연어 질문
- `--promote` : 답변이 재사용 가치 있으면 새 wiki 페이지로 저장 (사용자 승인)
- `--depth N` : 재귀 탐색 깊이 (기본 2 — wiki 페이지에서 링크된 paper-notes 까지)
- `--scope wiki|all` : wiki 만 (`wiki`) 또는 vault 전체 (`all`, 기본)

## Workflow

```
Q: 질문 입력
│
├─ Step 1: 07-wiki/index.md read (navigation catalog)
├─ Step 2: 관련 키워드로 wiki 페이지 후보 식별
├─ Step 3: 후보 wiki 페이지 read (entities/concepts/comparisons/syntheses)
├─ Step 4: depth 에 따라 linked paper-notes / 다른 wiki 페이지 read
├─ Step 5: (--scope all) 필요 시 04-areas/ 05-resources/ 08-raw/ 참조
├─ Step 6: 답변 합성 (citation 포함)
├─ Step 7: 답변 재사용성 평가 → --promote 시 새 wiki 페이지 제안
└─ Step 8: log.md 에 의미있는 query 기록
```

## Step-by-step

### Step 1: Wiki index 로 진입

```bash
cat "$VAULT/07-wiki/index.md"
```

Index 의 paper-notes / entities / concepts / comparisons / syntheses 섹션에서 질문 관련 키워드로 후보 추림.

### Step 2: 키워드 추출

질문에서 핵심 term 뽑기:
- Named entity (사람/조직/도구)
- Concept (method/algorithm/framework)
- Domain (composite / fatigue / DT / etc.)

각 term 에 대해 `07-wiki/` 에서 basename 매칭:
```bash
# 예: "composite fatigue 에 PINN 이 어떻게 쓰이나?"
grep -ril "pinn\|physics-informed" 07-wiki/
grep -ril "composite fatigue" 07-wiki/
```

### Step 3: 관련 wiki 페이지 read

후보 페이지 상위 5~10 개 read. Priority:
1. Syntheses (cross-cutting overview 먼저)
2. Concepts (method definitions)
3. Entities (people/orgs/tools)
4. Comparisons (A vs B)

### Step 4: 재귀 탐색 (depth 기반)

각 wiki 페이지의 `[[wikilinks]]` 수집 → 상위 k 개 추가 read. 
- `depth=1`: 직접 매칭 페이지만
- `depth=2` (기본): linked paper-notes 까지 포함
- `depth=3`: 2차 링크까지

### Step 5: Vault-wide 확장 (--scope all)

Wiki 에 답이 부족하면:
- `04-areas/(Concept) ...` (human-authored concepts)
- `05-resources/(Paper) ...` (human-curated papers)
- `08-raw/papers/{AuthorYear}.pdf` 원본 PDF (Read tool 로 개봉)
- Project 맥락 (`03-projects/Paper-1/` 등)

### Step 6: 답변 합성

**형식 규칙**:
- Markdown
- 각 주장은 `[[wikilink]]` 또는 `[[AuthorYear]]` 로 citation
- 서로 다른 source 가 충돌하면 명시 + 양쪽 citation
- 답변 끝에 "## Sources" 섹션 — 참조한 wiki 페이지 전체 list

**답변 템플릿**:
```markdown
## Answer

[답변 본문, 각 주장 뒤에 [[wikilink]] 또는 [[AuthorYear]] citation 삽입]

### Key claims

1. 주장 1 → [[source]]
2. 주장 2 → [[source]]

### Counterpoints / Open

- 명시적 반론 있으면 제시
- 불확실한 부분 플래그

## Sources consulted

- [[wiki page 1]] — 관련 부분
- [[wiki page 2]] — 관련 부분
- [[AuthorYear]] — 관련 paper
- (외부 vault 섹션 참조 시 경로 표기)
```

### Step 7: Promotion 평가

답변이 재사용 가치 있는지 판단 기준:
- 질문이 **generic**한가 (특정 세션 전용이 아님)
- 답변이 **여러 source 를 synthesize** 했는가
- 기존 wiki 에 **gap 이 있었는가** (이 답변이 gap 채움)
- 미래에 **재참조 가능성** 있는가

조건 충족 + `--promote` 지정 시:
1. 답변을 wiki 페이지 형식으로 재구성 (frontmatter + wikilink 풍부)
2. 적절한 type 판단 (보통 synthesis 또는 concept)
3. `07-wiki/{type}s/{Title}.md` 저장 제안
4. User 승인 후 저장 + index + log 업데이트

### Step 8: Log append

Meaningful query (≥2 wiki 페이지 참조 or 답변이 ≥300자) 시:
```markdown
## [YYYY-MM-DD] query | <question 요약> | <agent-id>
Sources: N wiki pages. Promoted: [[new-page]] (옵션).
```

## Interactive vs Batch

### Interactive (default)
- User 질문 → 답변 → optional promote discussion

### Batch (cron-friendly, 제한적 사용)
- `--batch file.md` : markdown 파일의 H2 섹션 각각을 질문으로 취급
- 답변을 `07-wiki/query-answers-YYYY-MM-DD.md` 에 모아 저장
- 자동 promote 는 하지 않음 (user 리뷰 필요)

## Cron 용도 (제한)

Query 는 기본적으로 interactive. Cron 으로 유용한 경우:

### Weekly synthesis refresh:
```bash
# 매주 월요일, "지난 주 ingest 된 paper-notes 로부터 research gap 찾기" 같은 고정 질문
0 9 * * MON claude -p "/query --scope wiki 'Based on paper-notes added in the last 7 days, what open research questions or contradictions emerged?'"
```

### Daily summary brief:
```bash
# 매일 오전, 오늘 언급될 만한 key papers brief
0 9 * * * claude -p "/query --depth 1 'What are the top 3 current research priorities in 07-wiki/ based on synthesis pages?'"
```

## 예시

**Q**: "composite fatigue 에서 PINN 이 어떻게 적용되나?"

**Flow**:
1. `07-wiki/index.md` → "PEML Spectrum for Section 3", "Physics-Informed Constitutive Modeling Landscape" 식별
2. 그 두 synthesis read
3. 링크된 paper-notes: [[Hao2025]], [[Kim2024]], [[Borkowski2023]] read
4. 답변 합성 with citations
5. 재사용 가치 판단 → promote 제안: "이 답변을 `07-wiki/concepts/PINN for Composite Fatigue.md` 로 저장?"

## Promotion 주의

- 답변이 기존 wiki 페이지와 **중복**이면 promote X
- 기존 페이지 **업데이트**가 더 적합하면 그 방향 제안
- Frontmatter `type:` 필수 (synthesis / concept / etc.)
- 새 페이지 생성 시 반드시 index.md + log.md 업데이트

## 관련 파일

- `07-wiki/_protocol.md` — wiki 운영 규칙
- `07-wiki/index.md` — 진입점
- `.claude/skills/wiki-lint/` — 답변 promote 후 orphan 검증
- `.claude/skills/deep-dive/` — 대안 (interactive 심화 토론)
