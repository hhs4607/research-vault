---
name: reading-tracker
description: Maintain `99-meta/reading-tracker.md` and related reading-progress views for the Research Vault. Use when the user wants reading status, next-paper suggestions, or tracker updates after paper review, note import, or literature-list maintenance.
---

# Reading Tracker

The tracker is a Markdown table first. If the user wants a Bases view and the `.base` file is missing, create it on demand.

## Commands

- `status`: summarize counts by status and phase in Korean
- `done <paper>`: mark a row as read, set the date, and fill takeaway if available
- `reading <paper>`: mark as currently reading
- `add <note-path>`: add one reviewed paper from an existing note
- `add-list <note-path>`: bulk-add entries from a literature list note
- `next`: propose the next unread paper by phase then priority
- `report`: generate a fuller Korean progress report

## Workflow

1. Read `99-meta/reading-tracker.md`.
2. Work against the Markdown table directly.
3. Preserve row order unless the user asks for reordering.
4. Output terminal or status text in Korean.

## Integration Rules

- After `paper-review`, if the paper already exists in the tracker, update the row automatically when the user wants it.
- Use the saved review note or discussion summary as the source for the `Takeaway` column.
- If the paper is missing from the tracker, ask before inserting a new row.

## Optional Base View

If `99-meta/reading-tracker.base` does not exist and the user wants a visual view, create a simple table base that points at the tracker note. Keep it minimal and aligned with the existing table columns.

## Guardrails

- Do not silently change phase or priority semantics.
- Keep emoji status values consistent with the existing table.
