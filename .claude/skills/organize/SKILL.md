---
name: organize
description: "Organize notes into PARA folders. Classifies by content type (Research/Idea/Study/Paper/Resource/Concept/Meeting), renames with category prefix, moves to correct folder, updates MOCs, fixes wikilinks, and suggests related notes."
---

# Organize Note (PARA)

Classify, rename, and move notes to the appropriate PARA folder. Handles both standalone notes and daily journal entries.

## Note Type Categories

| Category | Description | → PARA Folder |
|----------|-------------|---------------|
| **(Research)** | Active project work with goal/deadline (papers, implementations, applications) | `03-projects` |
| **(Idea)** | New ideas, hypotheses, implementation concepts (not yet a project) | `01-inbox` → promote to `03-projects` when developed |
| **(Study)** | Study logs, tutorial notes, course notes | Daily → `02-daily-notes` / Substantial → `04-areas` |
| **(Paper)** | Paper summaries, literature reviews | `05-resources` |
| **(Resource)** | Tool references, dataset descriptions, material summaries | `05-resources` |
| **(Concept)** | Concept explanations, methodology overviews (e.g., Digital Twin, CDM) | `04-areas` |
| **(Meeting)** | Meeting notes, discussion summaries, kickoff records | Daily → `02-daily-notes` / Formal → `03-projects` |

## Naming Rules

**Filename format:** `(Category) Readable Title.md`
- English category prefix in parentheses
- Title: English for technical terms, Korean for proper nouns (project names, Korean-specific terms)
- Daily notes: `YYYY-MM-DD-descriptive-topic.md`

**Examples:**
- `(Research) Paper-3 PINN Fatigue Degradation.md`
- `(Research) 포닥 논문 계획.md` — Korean proper noun
- `(Research) 2026 박사후 국내연수.md` — Korean proper noun
- `(Paper) Choi 2025 Multiscale Bayesian Fatigue.md`
- `(Concept) Digital Twin Composites.md`
- `(Resource) wtDigiTwin NREL.md`
- `(Idea) Physics-Informed Transformer.md`
- `(Study) Bayesian PINN Tutorial.md`
- `(Meeting) PI 주간 회의 Interface 모델.md` — Korean proper noun

**Title (frontmatter):** More descriptive version, Korean allowed.
- Example: filename `(Research) Paper-3 PINN Fatigue Degradation.md` → title `"Paper-3: PINN 기반 복합재 피로 Degradation 해석"`

## Prerequisites

All `obsidian` CLI commands require Obsidian to be running. PATH must include `/Applications/Obsidian.app/Contents/MacOS`.

## Workflow

### Step 1: Read & Validate

1. Read the note: `obsidian read path="01-inbox/note.md"`
2. Get current tags: `obsidian tags counts sort=count` (for taxonomy reference in Step 8)
3. Read `99-meta/tag-taxonomy.md` (canonical tag list)
4. Check frontmatter exists with required fields (title, date, tags)
5. Validate tags against taxonomy — flag any tags not in taxonomy
6. If frontmatter is missing or incomplete, generate and add it (tags from taxonomy only)

### Step 2: Classify

Determine two things:

**A. Content type** — Which category from the table above?
**B. Daily or standalone?**
- Daily (journal/log): personal record of activity on a specific day → `02-daily-notes`
- Standalone: reference, concept, or project note that lives independently → other PARA folders

Present classification with reasoning to user.

### Step 3: Rename (if needed)

Apply naming rules above. Show proposed rename and get user approval before proceeding.

### Step 4: Confirm

Show the full plan before executing:
```
Current:  01-inbox/old-filename.md
     →    04-areas/(Concept) New Title.md
```
Wait for user confirmation.

### Step 5: Move & Rename

Use `obsidian move` to move/rename in one step. This automatically updates all wikilinks across the vault.

```bash
# Move and rename
obsidian move path="01-inbox/old-name.md" to="05-resources/(Resource) New Title.md"

# Move only (keep filename)
obsidian move path="01-inbox/note.md" to="04-areas/"
```

- For daily notes: use `to="02-daily-notes/YYYY/MM/YYYY-MM-DD-topic.md"`
- For other notes: move directly to target folder with new name

**IMPORTANT**: `obsidian move` handles wikilink updates automatically. No manual wikilink fix step needed.

### Step 6: Update MOCs

**Both source AND target MOCs must be updated:**
1. **Source MOC** (e.g., `01-inbox/MOC.md`): Read and Edit to remove the note entry
2. **Target MOC** (e.g., `05-resources/MOC.md`): Append the entry:
   ```bash
   obsidian append path="05-resources/MOC.md" content="- [[(Resource) New Title]] — brief description"
   ```

### Step 7: Reconcile Tags

1. Get note's current tags: `obsidian tags path="05-resources/(Resource) New Title.md"`
2. Review against `99-meta/tag-taxonomy.md`
3. Update tags via `obsidian property:set name="tags" value="[tag1, tag2, tag3]" path="..."`
4. If no suitable tag exists, propose new tag → add to taxonomy first → apply to note
5. Keep 3-6 tags total

### Step 8: Suggest Related Notes

1. Search vault: `obsidian search query="keyword" limit=10`
2. Check backlinks: `obsidian backlinks path="05-resources/(Resource) New Title.md"`
3. Suggest 2-5 related notes with relationship type
4. Let user pick which to link
5. Append selected links: `obsidian append path="..." content="\n## 관련 노트\n- [[(Note)]] — relationship"`

## Batch Mode

When user requests organizing multiple notes (e.g., "inbox 정리해줘"):
1. List all notes in 01-inbox (excluding MOC.md)
2. For each note, show proposed: (Category) + target folder
3. Present full plan as a table
4. Execute after user confirms
