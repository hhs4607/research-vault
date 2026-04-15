## Core Files

- `CLAUDE.md`: intended vault workflow and note rules
- `README.md`: PARA folder overview
- `99-meta/tag-taxonomy.md`: canonical tags for new notes
- `99-meta/reading-tracker.md`: current literature queue
- Folder `MOC.md` files: update when a note is formally moved into or out of a PARA area

## PARA Structure

- `01-inbox/`: default landing zone for drafts, fresh captures, and new paper reviews
- `02-daily-notes/`: daily logs; avoid `obsidian daily:*` until the plugin path is fixed
- `03-projects/`: active, time-bounded work
- `04-areas/`: durable concept notes and ongoing responsibility areas
- `05-resources/`: papers, datasets, tooling, and reference material
- `06-archives/`: completed work
- `99-meta/`: taxonomy, tracker, attachments, scripts, and vault infrastructure

## Live interpretation rule

- Treat `01-inbox/` as in-progress working material unless the user explicitly says a note there is finalized.
- Treat notes outside `01-inbox/` as reusable reference/data assets by default, while still checking note-local status when needed.
- When synthesizing or merging paper content, do not assume inbox drafts override structured material already filed in `03-projects/`, `05-resources/`, `07-wiki/`, or `08-raw`.

## Note Family Rules

### New general notes

- Include frontmatter with at least `title`, `date`, `tags`, and `description`
- Prefer tags that already exist in `99-meta/tag-taxonomy.md`
- Default location is `01-inbox/` unless the user explicitly wants filing

### Existing review-note family

- The vault already contains review notes like `01-inbox/(Review) Wang et al 2023 - ...md`
- Preserve this family when adding adjacent literature review notes
- Do not force these notes into the formal `(Paper)` naming scheme unless the user asks

### Existing drift

- Some live notes use properties such as `created`, `paper`, `authors`, `year`, and `journal`
- Some live tags are outside the current taxonomy, including `review/paper`, `ai/piml`, and `fatigue/life-prediction`
- When editing an existing note, preserve working metadata unless there is a clear reason to repair it
- When creating a new note, prefer canonical tags, but note the drift if it affects nearby note consistency

## Obsidian CLI Guidance

- Prefer `obsidian read`, `obsidian search`, `obsidian file`, `obsidian move`, `obsidian append`, `obsidian property:set`, `obsidian tags`, and `obsidian tag`
- Verify commands against `obsidian help` if a feature is uncertain
- Avoid `obsidian daily:*` for durable notes in this vault because the current plugin path resolves to the vault root
- Use exact `path=` values when filenames are ambiguous

## MOC Update Policy

- If a note is only drafted in `01-inbox/`, adding it to `01-inbox/MOC.md` is optional
- If a note is formally moved between PARA folders, update both the source and target `MOC.md`
- Keep MOC entries short: `- [[Note Name]] — brief description`

## Tag Policy

- Read `99-meta/tag-taxonomy.md` before adding new canonical tags
- Check live usage with `obsidian tags counts sort=count`
- Do not remove or rename non-taxonomy tags across the whole vault unless the user explicitly asks for cleanup

## Paper Workflow Defaults

- Search Zotero first if the user mentions a paper title or author
- Use the paper review workflow for deep discussion, then save a review note in `01-inbox/`
- Offer reading-tracker updates after a review if the paper is already listed there
