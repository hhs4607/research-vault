---
name: project-status
description: "Generate a project status dashboard showing all active projects, their deadlines, progress, and next actions. Cross-references vault notes with Google Calendar deadlines. TRIGGER when: user asks 'project status', 'what's the progress', 'show my projects', 'deadline check', 'project dashboard', 'how are my projects going', or asks about specific project progress."
---

# Project Status Dashboard

Generate a status report for active research projects.

## Workflow

### Step 1: Scan Projects

Read all files in `03-projects/` and extract:
- Project title and type (Research, Career, Meeting)
- Deadline (if stated in note)
- Current status indicators (from note content)
- Last modified date
- Related papers/resources (internal links)

### Step 2: Cross-Reference Calendar

Check Google Calendar for:
- Upcoming deadlines matching project names
- Conference dates
- Meeting schedules related to projects

### Step 3: Assess Progress

For each project, determine status:
- **On Track**: Active work, deadline comfortable
- **At Risk**: Deadline within 14 days, incomplete milestones
- **Overdue**: Past deadline
- **Blocked**: Waiting on external input
- **Inactive**: No updates > 30 days

### Step 4: Generate Dashboard

Display to user and optionally save to vault:

```markdown
# Project Dashboard — YYYY-MM-DD

## Summary
| Status | Count |
|--------|-------|
| On Track | N |
| At Risk | N |
| Overdue | N |

## Active Projects

### [Priority] Project Title
- **Status**: On Track / At Risk / Overdue
- **Deadline**: YYYY-MM-DD (N days remaining)
- **Progress**: Brief description
- **Next Action**: What needs to happen next
- **Related Notes**: [[links]]

---

## Upcoming Deadlines (next 30 days)
| Date | Project | Action Required |
|------|---------|----------------|

## Inactive Projects (> 30 days)
- Project name — last activity date — suggested action
```

### Step 5: Alerts

Highlight critical items:
- Deadlines within 3 days → **URGENT**
- Deadlines within 7 days → **ATTENTION**
- Stale projects → suggest archive or reactivation

## Rules

- Do not fabricate progress — report only what's observable from notes and calendar
- If a project note lacks a clear deadline, flag it rather than guessing
- Sort projects by deadline urgency (nearest first)
- Include postdoc application deadline (2026-04-13) as a tracked item
