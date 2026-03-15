---
name: tag
description: "Manage the vault's tag taxonomy (99-meta/tag-taxonomy.md). View all tags, add new tags, merge duplicates, rename tags across vault, and audit for inconsistencies."
---

# Tag Taxonomy Manager

Manage the vault-wide tag taxonomy at `99-meta/tag-taxonomy.md`.

## Prerequisites

All `obsidian` CLI commands require Obsidian to be running. PATH must include `/Applications/Obsidian.app/Contents/MacOS`.

## Commands

### /tag (no args) — View Taxonomy
1. Get live vault tag stats: `obsidian tags counts sort=count`
2. Read and display `99-meta/tag-taxonomy.md` grouped by category
3. Show side-by-side comparison of taxonomy vs actual usage

### /tag add [tag] [description]
1. Check if tag already exists: `obsidian tag name="category/name" total`
2. If exists, inform user and show existing description + usage count
3. If new, add to the correct category section in `99-meta/tag-taxonomy.md`
4. Follow format: `- \`category/name\` — Description`

### /tag merge [source-tag] [target-tag]
1. Confirm with user: "Merge `source-tag` into `target-tag`?"
2. Find all notes using source tag: `obsidian tag name="source-tag" verbose`
3. For each note, update tags: `obsidian property:set name="tags" value="[updated tags]" path="..."`
4. Remove `source-tag` from taxonomy
5. Report: which notes were updated

### /tag rename [old-tag] [new-tag]
1. Confirm with user
2. Update tag in `99-meta/tag-taxonomy.md`
3. Find all notes: `obsidian tag name="old-tag" verbose`
4. Update each note: `obsidian property:set name="tags" value="[updated tags]" path="..."`
5. Report: which notes were updated

### /tag audit
Run all checks using CLI data and report:

1. **Orphan tags**: Compare `obsidian tags counts` against `99-meta/tag-taxonomy.md`
   - Tags in vault but NOT in taxonomy
   - Action: Suggest adding to taxonomy or replacing with existing tag
2. **Dead tags**: Tags in taxonomy but with zero count in `obsidian tags counts`
   - Action: Suggest removal or note which notes should have them
3. **Over-tagged notes**: Check each note's tag count via `obsidian tags path="..."`
   - Notes with more than 6 tags
   - Action: Suggest which tags to remove
4. **Under-tagged notes**: Notes with fewer than 3 tags
   - Action: Suggest which tags to add

### /tag cleanup
Interactive cleanup session:
1. Run audit
2. For each issue, propose fix and ask user
3. Execute approved fixes using `obsidian property:set`

## Rules

- Taxonomy file is the single source of truth
- Tags follow `category/subcategory` format
- Maximum 6 tags per note, minimum 3
- When merging or renaming, always update ALL notes in vault
