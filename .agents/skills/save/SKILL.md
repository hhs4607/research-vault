---
name: save
description: Save external content such as web pages, YouTube material, or raw text into the Research Vault with frontmatter, tags, and related-note suggestions. Use when the user wants material captured into `01-inbox/` for later research use rather than only summarized in chat.
---

# Save

Use `defuddle` for ordinary web pages when possible. Read `../research-vault-harness/references/vault-conventions.md` before creating the note.

## Workflow

1. Detect the source:
   - YouTube URL
   - ordinary web URL
   - raw pasted text

2. Extract content:
   - YouTube: use subtitles or the best available transcript path
   - web page: use `defuddle` first, then direct web fetch only if needed
   - raw text: use the supplied text directly

3. Translate or summarize into Korean when the source is not Korean and the user has not asked to preserve the original language.

4. Create a note in `01-inbox/` with:
   - `title`
   - `date`
   - `tags`
   - `description`
   - `source` when applicable
   - optional `author` or `channel`

5. Choose 3-6 tags from the taxonomy when possible.

6. Suggest 2-5 related notes from the vault and append them as wikilinks if the user wants the links saved immediately.

7. Offer the next step:
   - `deep-dive`
   - `organize`
   - stop after save

## Guardrails

- Save first, organize later unless the user asks for both in one pass.
- Do not invent unsupported claims while restructuring source content.
