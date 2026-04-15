---
name: organize
description: Classify, rename, move, and relink notes within the Research Vault PARA structure while keeping MOCs and Obsidian links coherent. Use when a note should be promoted out of inbox, when the user asks for PARA organization, or when a saved review, resource, or concept note needs formal filing.
---

# Organize

Read `../research-vault-harness/references/vault-conventions.md` before moving anything.

## Workflow

1. Read the target note and inspect nearby note families in the destination folder.

2. Classify it into one of the vault's live buckets:
   - keep in `01-inbox/` if it is still a draft
   - if the note already belongs to a live paper workspace under `01-inbox/`, prefer reorganizing it in place inside that workspace (for example creating subsection folders plus a local `README.md` index) rather than promoting it to `03-projects/` just because the cluster has grown
   - `03-projects/` for active, time-bounded work that is actually being promoted into the formal Projects layer
   - `04-areas/` for durable concepts or ongoing responsibilities
   - `05-resources/` for papers, datasets, and reference materials
   - `06-archives/` only when the user explicitly wants archival
   - `08-raw/` only for original-source or raw archival material; if the user explicitly wants obsolete draft versions moved out of inbox but still preserved as lineage artifacts, prefer a subfolder such as `08-raw/draft-lineage/`

   Special case for version-lineage draft moves:
   - if the user asks to "넘겨버려", archive, or clear old draft versions from `01-inbox/` while keeping them available for comparison, move those version files into `08-raw/draft-lineage/`
   - after the move, update any explicit path mentions like `01-inbox/...` in handoff docs, project hubs, and analysis notes to the new raw path
   - add or update `08-raw/MOC.md` when the raw area becomes a deliberate archive surface

3. Propose:
   - current path
   - target path
   - rename if needed
   - whether source and target MOCs should change

4. Preserve live note families:
   - a fresh paper review can remain `(Review)` in `01-inbox/`
   - if the user explicitly promotes a literature review into `05-resources/`, consider renaming it to the `(Paper)` family for consistency, but confirm first
   - do not force all legacy notes into one naming scheme

5. Execute with `obsidian move` when possible so wikilinks stay updated:

```bash
obsidian move path="01-inbox/example.md" to="05-resources/(Paper) Example.md"
```

6. Update MOCs when the move is formal:
   - remove the old entry from source `MOC.md` if present
   - append one concise line to target `MOC.md`

7. Reconcile frontmatter and tags only as much as needed for the new home. Do not silently rewrite every legacy field.

8. For intra-workspace reorganization of many related notes:
   - create or update a local index note such as `README.md` for the cluster
   - if the user mainly wants a folder map, writing guide, or blank scaffold for an active workspace, prefer creating that folder-local `README.md` first
   - when the workspace is actively being used and the user says not to touch other files, keep the change isolated to the target folder instead of adding structure notes to a separate master project note
   - move notes into clear subfolders by section/theme
   - update the parent workspace `README.md` and `worklog.md` only when the user wants broader reorganization, not when they asked for a minimal local scaffold
   - prefer linking to existing durable wiki/synthesis notes instead of duplicating them into the workspace

## Guardrails

- Confirm before bulk-moving multiple notes.
- Avoid `obsidian daily:*` in this vault.
- If the move would break an established project structure, stop and surface the tradeoff instead of guessing.
- Do not bury folder-structure guidance inside a complex project dashboard when a folder-local `README.md` would let the user see the structure immediately.
