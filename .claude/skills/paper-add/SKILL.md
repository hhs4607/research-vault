---
name: paper-add
description: Find a paper online, download PDF via Chrome crawling, and add to Zotero
argument-hint: [DOI or paper title or reference text]
---

# Paper Add — Find, Download, and Add to Zotero + Raw

Find a paper online using APIs + headless Chrome crawling, download the PDF, register it in the local Zotero library, **and copy the PDF to `08-raw/papers/{AuthorYear}.pdf`** (vault's raw layer).

**Save locations (2026-04-15 update)**:
- Zotero storage: `~/Zotero/storage/{key}/{filename}.pdf` (Zotero managed)
- Vault raw: `08-raw/papers/{AuthorYear}.pdf` (vault immutable raw layer) — **MANDATORY**
- See `08-raw/_protocol.md` for raw layer rules.

**Input:** $ARGUMENTS (DOI, paper title, or a full reference citation)

## Step 1: Parse Input

Determine what the user provided:
- **DOI** (e.g., `10.1007/s00707-013-1057-1`) → go to Step 3
- **Paper title** → go to Step 2
- **Full citation** (e.g., `Zhang D, Waas AM. A micromechanics... Acta Mech 2014`) → extract title and author, go to Step 2

## Step 2: Find DOI (if not provided)

If only title/author is given, search Semantic Scholar API to find the DOI:

```bash
python3 "<vault>/.claude/skills/paper-add/paper_add.py" \
  --title "paper title keywords" \
  --author "LastName" \
  --no-download
```

This will search and print the DOI. If not found, try WebSearch as fallback.

## Step 3: Run Paper Add Script

**IMPORTANT:** Zotero desktop app must be CLOSED before running this (SQLite locking).

Warn the user: "Zotero 앱을 닫아주세요. DB에 직접 추가합니다."

Then run:

```bash
python3 "<vault>/.claude/skills/paper-add/paper_add.py" --doi "THE_DOI"
```

Or with title search:
```bash
python3 "<vault>/.claude/skills/paper-add/paper_add.py" --title "keywords" --author "LastName"
```

The script will:
1. Fetch metadata from CrossRef API
2. Search for open access PDF via Unpaywall API
3. If not found, crawl with headless Chrome (Google Scholar → ResearchGate → Publisher)
4. Download PDF if found
5. Create Zotero storage entry + insert into SQLite

Replace `<vault>` with the actual vault path (working directory).

## Step 3b: Copy PDF to Vault Raw Layer (MANDATORY)

After Zotero registration succeeds, **copy the PDF** to `08-raw/papers/{AuthorYear}.pdf`:

```bash
# Get AuthorYear from metadata (firstAuthor lastName + year)
AUTHOR_YEAR="Hao2025"    # 예시 — 실제는 metadata 에서 추출

# Find Zotero storage path (script output) — typically ~/Zotero/storage/{8-char-key}/{filename}.pdf
ZOTERO_PDF="/mnt/c/Users/EMDOL/Zotero/storage/XXXXXXXX/paper.pdf"

# Check if already exists (prevent duplicate)
if [ ! -f "<vault>/08-raw/papers/${AUTHOR_YEAR}.pdf" ]; then
  cp "$ZOTERO_PDF" "<vault>/08-raw/papers/${AUTHOR_YEAR}.pdf"
  echo "Raw PDF: 08-raw/papers/${AUTHOR_YEAR}.pdf"
else
  echo "Raw PDF already exists: 08-raw/papers/${AUTHOR_YEAR}.pdf (skip)"
fi
```

**중복 처리**:
- 같은 AuthorYear 다른 논문: `{AuthorYear}b.pdf`, `{AuthorYear}c.pdf` (paper-notes 네이밍과 일치)
- 이미 raw 에 있고 paper-notes 도 있으면 → 이 paper 는 이미 ingested. Duplicate add 경고.

**PDF 가 다운로드되지 않았을 때**: Zotero 등록만 완료. 사용자에게 수동 다운로드 안내 (Step 4). raw copy 는 추후 PDF 확보 후 수동 실행.

## Step 4: Report Results

After the script completes, present:

```
## Paper Added to Zotero

**Title:** [title]
**Authors:** [authors]
**Journal:** [journal] ([year])
**DOI:** [doi]
**PDF:** attached / not found

[If PDF not found:]
PDF를 찾지 못했습니다. 다음 방법으로 직접 추가하세요:
1. GIST 도서관: https://doi.org/[doi] (VPN 필요할 수 있음)
2. Google Scholar: [link]
3. 다운로드 후 Zotero에서 해당 항목에 드래그앤드롭

Zotero를 다시 열면 새 항목이 보입니다.
```

## Step 5: Suggest Next Actions

- "Run `/paper-search [title]` to verify the paper was added"
- "Run `/paper-review [title]` to start a review discussion **→ creates 07-wiki/paper-notes/{AuthorYear}.md**"
- "Paper 는 이제 (1) Zotero library, (2) 08-raw/papers/{AuthorYear}.pdf 양쪽에 저장됨. 다음 단계로 해석 노트를 07-wiki/paper-notes/ 에 만들려면 /paper-review 실행"

## Ingest 완결 체크리스트 (스킬 체인 확인용)

Ingest 한 단일 paper 의 최종 상태:

- [ ] `08-raw/papers/{AuthorYear}.pdf` 존재 (raw 원본)
- [ ] Zotero library 에 등록 (bibliographic management)
- [ ] `07-wiki/paper-notes/{AuthorYear}.md` 존재 (해석 노트)
- [ ] `07-wiki/index.md` 에 `[[AuthorYear]]` 엔트리 추가
- [ ] `07-wiki/log.md` 에 ingest 로그 추가
- [ ] (선택) 관련 entity/concept/synthesis 페이지 업데이트

`paper-add` 는 1~2 단계 담당. `paper-review` 가 3~5 단계 담당. 4~5 는 paper-review 에서 자동화 (2026-04-15 패치).
