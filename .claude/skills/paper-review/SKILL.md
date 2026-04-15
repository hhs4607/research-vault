---
name: paper-review
description: "[DEPRECATED 2026-04-15] Use /ingest --mode deep instead. Interactive paper review — legacy, schema 없음."
argument-hint: "[search term | DOI | URL | vault note title]"
status: deprecated
deprecated_at: 2026-04-15
redirect: "/ingest <DOI|URL> --mode deep  (Paper-1 관련 paper 는 --mode paper1 --section ... --tier ...)"
reason: "ingest 는 Paper-1 schema 준수 + Paper-1 PROTOCOL 통합 + cron-ready. paper-review 는 legacy interactive mode 만 유니크, Phase 3 에서 ingest --interactive 로 통합 예정"
---

# Paper Review — [DEPRECATED]

**⚠️ 이 스킬은 DEPRECATED 됨.** 2026-04-15 결정 — `ingest` 스킬이 상위 호환.

**대체**:
- 일반 paper: `/ingest <DOI|URL> --mode deep`
- Paper-1 reference: `/ingest <DOI|URL> --mode paper1 --section §N.M --tier X --role anchor`

자세한 내용: [[../../../99-meta/llm-skill-playbook|LLM Skill Playbook]] §4

---

# Paper Review — Deep Review + Discussion + Auto-Save

Load a paper from Zotero, DOI, URL, or existing vault note, conduct an interactive review discussion, then automatically save the review note.

**Save location (2026-04-15 update)**: `07-wiki/paper-notes/{AuthorYear}.md`. NOT `01-inbox/`. See `07-wiki/_protocol.md`.

**Must-read before executing**: `07-wiki/_protocol.md` (wiki 운영 규칙).

**Input:** $ARGUMENTS — one of:
- Zotero search term (title, author, collection name)
- DOI (e.g., `10.1016/j.ijmecsci.2025.110723`)
- URL (e.g., `https://arxiv.org/abs/...` or ScienceDirect link)
- Vault note title (e.g., `(Paper) Hao 2025 d-PINN...`)

## Step 0: Detect Input Type

Determine the input type from $ARGUMENTS:

```
if starts with "10." or "doi:" → DOI mode
if starts with "http" → URL mode
if matches "(Paper)" or exists as vault .md file → Vault note mode
else → Zotero search mode
```

### DOI Mode
1. Resolve DOI via WebFetch: `https://doi.org/[DOI]`
2. Extract metadata (title, authors, abstract, journal)
3. If PDF available (open access / arXiv), read it
4. If paywalled, work with abstract + any available metadata
5. Check if paper already exists in Zotero → if yes, switch to Zotero mode
6. Skip to Step 3 (Load Paper Metadata)

### URL Mode
1. Fetch content via WebFetch or Playwright (for JS-rendered pages)
2. Extract metadata from the page
3. If arXiv: also fetch PDF via Read tool
4. Skip to Step 3

### Vault Note Mode
1. Read the existing vault note
2. Extract metadata from frontmatter (title, DOI, source, tags)
3. If DOI exists in frontmatter, optionally fetch full paper for deeper review
4. Skip to Step 5 (present briefing based on existing note content + any new data)

### Zotero Search Mode (original behavior)
Continue to Step 1 below.

## Step 1: Locate Zotero Data Directory

Detect the Zotero data directory automatically based on the OS:

```bash
OS="$(uname -s)"
case "$OS" in
  Linux*)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r')
      ZOTERO_DIR="/mnt/c/Users/${WIN_USER}/Zotero"
    else
      ZOTERO_DIR="$HOME/Zotero"
    fi
    ;;
  Darwin*)
    ZOTERO_DIR="$HOME/Zotero"
    ;;
esac
```

If the directory is not found at the expected location, search for `zotero.sqlite` under the user's home directory to locate it.

## Step 2: Search Zotero Database

Query `zotero.sqlite` to find matching papers. Search across titles, creators, and collection names. If multiple results are found, present a numbered list and ask the user to choose.

## Step 3: Load Paper Metadata

For the selected paper, extract full metadata: title, authors, date, DOI, journal, abstract, tags, and PDF attachment path.

The PDF path format is `storage:filename.pdf`. The actual file is at:
`{ZOTERO_DIR}/storage/{attachment_key}/{filename}`

## Step 4: Read the PDF

Use the Read tool to read the PDF file. Focus on extracting:
- Abstract
- Introduction (research gap and motivation)
- Methodology (key approach)
- Results (main findings)
- Discussion and Conclusions

## Step 5: Present Briefing and Start Discussion

Present a structured briefing to the user:

```
## [Paper Title]
**Authors:** [list] | **Year:** [year] | **Journal:** [journal]

### One-line Summary
[What this paper does in one sentence]

### Key Contributions (3 items max)
1. ...
2. ...
3. ...

### Methodology
[Brief description of the approach]

### Limitations
- [Author-acknowledged limitations]
- [Your observed limitations]

---

### Discussion Topics
I'd like to discuss these aspects with you:

1. **[Topic 1]** — [Why this is interesting/debatable]
2. **[Topic 2]** — [Connection to your research area]
3. **[Topic 3]** — [Potential gap or extension]

Which topic interests you, or do you have your own topic to start with?
```

## Step 6: Interactive Discussion

After presenting the briefing, engage in natural conversation. Both you and the user can propose new discussion topics. Continue until the user indicates the discussion is complete (e.g., "done", "save", "끝", "저장", or moves to a new task).

## Step 7: Auto-Save Note (after discussion ends)

When the discussion concludes, automatically create a review note:

### 7-1. Read Tag Taxonomy
Read `99-meta/tag-taxonomy.md` from the vault and select 3-6 appropriate tags.

### 7-2. Search for Related Notes
Search the Obsidian vault for related notes by key terms from the paper. Suggest 2-5 wikilinks.

### 7-3. Create the Note (07-wiki/paper-notes/ REQUIRED)

**IMPORTANT (2026-04-15 update)**: Paper notes are **interpreted data** and MUST be saved to `07-wiki/paper-notes/`, NOT `01-inbox/` or `08-raw/`. See `07-wiki/_protocol.md` and `08-raw/_protocol.md`.

Save to `07-wiki/paper-notes/` with filename format: `{FirstAuthor}{Year}.md` (e.g., `Kim2024.md`, `Hao2025.md`, `Chaboche1988b.md`).

**중복 체크 필수**: 생성 전 `ls 07-wiki/paper-notes/{AuthorYear}*.md` 확인. 이미 있으면 update 로 전환 (overwrite 금지, append/merge).

Note template:

```markdown
---
type: paper-note
citation_key: "[AuthorYear]"
doi: "[DOI]"
title: "[Paper Title]"
authors: "[First Author et al.]"
year: [YYYY]
journal: "[Journal name]"
volume: "[Volume]"
pages: "[Pages]"
sections: ["[Paper-1 section where used, e.g., §3.2 Physics-Informed]"]
keywords: [selected/keywords]
source: "[Zotero / DOI manual / master list / etc.]"
pdf_available: [true/false]
pdf_path: "08-raw/papers/[AuthorYear].pdf"
oa_status: "[open / closed]"
citation_count: 0
date_created: [today's date]
date_updated: [today's date]
tags: [selected/tags, from/taxonomy]
description: "[1-2 sentence Korean summary]"
zotero-key: "[Zotero item key]"
---

## Summary

[2-3 paragraph summary of the paper — what it does, how, and why it matters]

## Key Contributions

1. [Contribution 1]
2. [Contribution 2]
3. [Contribution 3]

## Methodology

[Description of the approach, models, experiments]

## Discussion Points

### [Topic 1 Title]
- **Question/Issue:** [What was discussed]
- **Key Arguments:** [Points made by both sides]
- **Conclusion:** [What we agreed on or remains open]

### [Topic 2 Title]
...

[Repeat for each discussion topic]

## My Insights

- [Connection to user's research]
- [Ideas sparked by the discussion]
- [Potential applications or extensions]
- [Follow-up actions]

## Limitations

- [Paper's acknowledged limitations]
- [Limitations identified during discussion]

## Related Notes

- [[Related Note 1]]
- [[Related Note 2]]
```

### 7-4. Update Wiki Index + Log (MANDATORY)

After saving the paper-note, **automatically**:

1. Append to `07-wiki/index.md` under `## Paper-notes` section:
   ```
   - [[AuthorYear]] — 한 줄 요약 (description frontmatter 재사용)
   ```
   If `## Paper-notes` section doesn't exist, create it in alphabetical order with other type headers.

2. Append to `07-wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] ingest | AuthorYear | <agent-id>
   [1-line reason, e.g., "§3.2 PINN anchor paper review"]
   ```

3. Suggest related wiki pages to update:
   - If new entity/org/tool encountered → `07-wiki/entities/`
   - If new method/concept → `07-wiki/concepts/`
   - If fits existing synthesis → update that synthesis page

### 7-5. Confirm and Suggest Follow-up

After saving, show:
- File path: `07-wiki/paper-notes/{AuthorYear}.md`
- Index + log updated (confirm)
- Tags applied
- Related wiki pages suggested (entity/concept/synthesis)

Then suggest (in order):
1. PDF 원본이 `08-raw/papers/{AuthorYear}.pdf` 에 있는지 확인 — 없으면 `/paper-add` 로 저장
2. Detailed discussion 이 필요하면 `/deep-dive` 로 이어가기
3. Paper-1 같은 프로젝트에서 인용 예정이면 `03-projects/Paper-1/references/ch-N-*/refs.md` 의 spine 테이블에 추가

## Step 8: Post-Actions

After note is saved, offer these follow-up actions:

### 8-1. Update Reading Tracker
If `99-meta/reading-tracker.md` exists, check if this paper is in the tracker:
- If found → auto-update status to `✅ 읽음`, fill takeaway from Discussion Points
- If not found → ask: "Reading tracker에 추가할까요?"

### 8-2. Suggest Zotero Add
If paper was reviewed via DOI/URL mode (not from Zotero):
- Suggest: "이 논문을 Zotero에도 추가할까요? → /paper-add [DOI]"

### 8-3. Suggest Related Reviews
Search vault for other papers in the same Paper-1 section:
- "같은 Ch.2.2 섹션의 다른 논문도 리뷰할까요? → /paper-review [next paper]"
