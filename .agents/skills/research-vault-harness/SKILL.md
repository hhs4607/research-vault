---
name: research-vault-harness
description: Shared operating rules and utilities for this specific Obsidian Research Vault. Use when Codex is working inside this vault on Zotero-backed literature review, Obsidian note creation or editing, PARA organization, tag maintenance, reading-tracker updates, or any workflow that needs local vault conventions instead of generic Markdown behavior.
---

# Research Vault Harness

Use this skill as the first layer for vault-specific work. It explains the live conventions, points to the reusable Zotero helper, and routes work to the task-specific skills in `.agents/skills/`.

## Quick Start

- Read [vault-conventions.md](references/vault-conventions.md) before editing notes, moving files, or changing tags.
- Use [zotero-helper.md](references/zotero-helper.md) and `scripts/zotero_helper.py` before writing ad-hoc Zotero SQL.
- Prefer the existing `obsidian-cli` and `obsidian-markdown` skills for note operations and Obsidian-flavored Markdown syntax.

## Workflow Router

- Paper lookup or shortlist: use `paper-search`
- Deep paper discussion plus saved review note: use `paper-review`
- DOI/title-based Zotero ingestion: use `paper-add`
- PARA classification, rename, move, and MOC maintenance: use `organize`
- Reading queue maintenance: use `reading-tracker`
- Tag audit or taxonomy changes: use `tag`
- Save external content into the vault: use `save`
- Expand a note through structured synthesis: use `deep-dive`
- Verify a ChatGPT share link and map findings to research notes: use `chatgpt-factcheck`

## Guardrails

- Do not assume `CLAUDE.md` matches the live vault perfectly. Follow the note family already in use when editing existing material.
- Do not run `obsidian daily:*` for durable filing until the daily note path is corrected.
- Do not normalize the entire tag system unless the user asks; the live vault already contains non-taxonomy tags.
- Default new material to `01-inbox/` unless the user asks for filing or the workflow explicitly includes organization.

## Shared Resources

- `references/vault-conventions.md`: PARA layout, note-family behavior, tag drift, and Obsidian CLI caveats
- `references/zotero-helper.md`: reusable commands for local Zotero discovery and metadata lookup
- `scripts/zotero_helper.py`: JSON-emitting helper for Zotero locate/search/item operations

## Example Commands

```bash
python3 .agents/skills/research-vault-harness/scripts/zotero_helper.py locate
python3 .agents/skills/research-vault-harness/scripts/zotero_helper.py search --query "high-performance composites" --limit 5
python3 .agents/skills/research-vault-harness/scripts/zotero_helper.py item --item-id 1491
```
