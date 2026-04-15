---
name: daily-briefing
description: "Generate a morning briefing combining today's Google Calendar schedule, pending tasks, upcoming deadlines, inbox status, and reading tracker progress. Creates or updates a daily note in the vault. TRIGGER when: user says 'briefing', 'today's schedule', 'daily note', 'what's on today', 'morning update', 'check my day', 'agenda', or asks about today's plan. Also trigger at start of any new work session."
---

# Daily Briefing

Generate a comprehensive daily briefing and create/update the daily note.

## Workflow

### Step 1: Gather Data (parallel)

Collect from multiple sources simultaneously:

1. **Google Calendar**: Fetch today's events (time, title, location, attendees)
2. **Vault Inbox**: Count and list unprocessed items in `01-inbox/`
3. **Project Deadlines**: Scan `03-projects/` for deadlines within 7 days
4. **Reading Tracker**: Check `99-meta/reading-tracker.md` for pending papers
5. **Yesterday's Note**: Read the most recent daily note for carry-over tasks

### Step 2: Compile Daily Note

Create file at `02-daily-notes/YYYY/MM/YYYY-MM-DD.md` with this structure:

```markdown
---
title: "Daily Note — YYYY-MM-DD (Day)"
date: YYYY-MM-DD
tags:
  - daily
description: "Daily briefing and work log"
---

# YYYY-MM-DD (Day of Week)

## Schedule
| Time | Event | Location |
|------|-------|----------|
| HH:MM | Event name | Location |

## Deadlines (next 7 days)
- [ ] Project — Deadline date — Status

## Inbox Triage (N items)
- [ ] Note name — suggested action

## Reading Queue
- Next priority paper from reading-tracker
- Papers in progress

## Tasks
- [ ] Carry-over from yesterday
- [ ] New tasks

## Log
_(workspace for today's notes)_
```

### Step 3: Present Summary

Display a concise briefing to the user:
- Today's event count and first event
- Critical deadlines (within 3 days)
- Inbox count
- Suggested focus for the day

## Rules

- If daily note already exists for today, append new information rather than overwriting
- Always use `02-daily-notes/YYYY/MM/` path, never vault root
- Dates in frontmatter use ISO 8601 format (YYYY-MM-DD)
- If Google Calendar is unreachable, create note with "[Calendar sync pending]" placeholder
