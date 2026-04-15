---
name: paper-review
description: Review a paper from Zotero, DOI, URL, or an existing vault note, discuss it with the user, and save a structured review note in the Research Vault. Use when the user wants deep paper analysis rather than a quick lookup, especially for literature review, Paper-1 connections, or discussion-driven note creation.
---

# Paper Review

Read `../research-vault-harness/references/vault-conventions.md` first. Use `../research-vault-harness/scripts/zotero_helper.py` for local Zotero metadata, `pdftotext` for attached PDFs, and `obsidian-cli` or direct file edits to save the note.

## Input Modes

- DOI: resolve metadata online; if the paper already exists in Zotero, switch to Zotero mode
- URL: fetch metadata and body text; prefer official paper pages
- existing vault note: read the note and extend or refine it
- search term: search Zotero first and let the user choose when multiple hits exist

## Workflow

1. Resolve the paper:
   - for search terms, run `paper-search` logic or call the shared Zotero helper directly
   - for a selected Zotero record, fetch full metadata with `zotero_helper.py item`
   - prefer an attached PDF when one exists

2. Read the paper:
   - inspect the PDF with `pdfinfo`
   - extract text with `pdftotext <pdf> -`
   - focus on abstract, introduction, methodology, results, discussion, and conclusion
   - if the PDF is unavailable, work from abstract plus metadata and state the limitation clearly

3. Start the discussion with a compact briefing:
   - one-line summary
   - 3 key contributions at most
   - methodology snapshot
   - limitations
   - 2-4 discussion hooks tied to the user's research notes when possible

4. Discuss interactively until the user signals to save, stop, or move on.

5. Save the review note to `01-inbox/` using the established review-note family:
   - filename: `(Review) FirstAuthor et al YEAR - Short Topic.md`
   - preserve continuity with existing review notes instead of forcing a new family

6. Frontmatter for a new review note should combine live-family compatibility with useful canonical fields:

```yaml
---
title: "Paper review title"
date: 2026-04-02
tags:
  - engineering/composites
  - research/fatigue
  - ai/surrogate
created: 2026-04-02
paper: "Full paper title"
authors: "Surname, Surname, Surname"
year: 2024
journal: "Journal name"
doi: "10...."
zotero-key: "ITEMKEY"
description: "1-2 sentence Korean summary"
source: "https://doi.org/..."
---
```

7. Body structure:
   - `## Paper 정보`
   - `## One-line Summary`
   - `## 핵심 구조` or `## Key Contributions`
   - `## Methodology`
   - `## Limitations`
   - `## Paper-1 연결 분석` when relevant
   - `## 추가 논의 필요 사항`
   - `## 핵심 인용 후보` when useful
   - `## Related Notes`

8. Search the vault for 2-5 related notes and add wikilinks.

9. After saving, offer:
   - reading-tracker update
   - `organize` if the user wants filing beyond inbox
   - next review candidate from the same Paper-1 section

## Guardrails

- Preserve strong claims for text actually supported by the paper.
- If discussion draws on inference rather than explicit text, label it as interpretation.
- If multiple papers match the search term, stop and let the user choose instead of guessing.
