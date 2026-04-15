---
name: tag
description: Inspect, add, rename, merge, and audit tags against `99-meta/tag-taxonomy.md` while respecting the live tag drift already present in the vault. Use when the user wants taxonomy maintenance, tag cleanup, or tag assignment decisions for new notes.
---

# Tag

Read `../research-vault-harness/references/vault-conventions.md` first.

## Workflow

1. Read `99-meta/tag-taxonomy.md`.
2. Check live usage with:

```bash
obsidian tags counts sort=count
```

3. Distinguish between:
   - canonical tags in the taxonomy
   - live tags already used in notes but not yet normalized

4. Common operations:
   - add: register a new canonical tag in the taxonomy
   - rename: change a canonical tag and update notes that should follow it
   - merge: move notes from a source tag into a target tag
   - audit: report mismatches, dead tags, under-tagged notes, and over-tagged notes
   - cleanup: interactive follow-up from an audit, never silent mass cleanup

## Assignment Rules

- For new notes, prefer 3-6 tags from the taxonomy.
- For legacy review notes, tolerate existing out-of-taxonomy tags when preserving note-family continuity.
- Do not strip useful legacy tags from a note unless the user asks for cleanup.

## Guardrails

- Do not assume every live tag outside the taxonomy is wrong.
- Confirm before renaming or merging tags across the whole vault.
