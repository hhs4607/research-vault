---
name: reading-tracker
description: "Track reading progress of literature lists using Obsidian Bases. Create/update reading status, add notes, filter by phase/paper/status."
argument-hint: "[status | done <title> | add <note-path> | phase <n>]"
---

# Reading Tracker — Literature Progress Management

Track reading progress of collected literature using Obsidian Bases (.base) for visual table/card views.

**Input:** $ARGUMENTS — subcommand + optional args

## Subcommands

### `status` (default, no args)
Show current reading progress summary in terminal.

### `done <paper-title-or-#>`
Mark a paper as read. Prompts for a one-line takeaway note.

### `reading <paper-title-or-#>`
Mark a paper as currently reading.

### `add <note-path>`
Add a new paper from an existing vault note to the tracker.

### `add-list <note-path>`
Bulk-add all papers from a literature list note (scans for DOI/URL table rows).

### `phase <n>`
Filter and show only papers in the given phase.

### `next`
Show the next unread paper in priority order.

### `report`
Generate a reading progress report for terminal output (Korean).

---

## Data Storage

### Tracker Note: `99-meta/reading-tracker.md`

Central tracking file with YAML frontmatter table. All paper entries stored here.

```yaml
---
title: "Literature Reading Tracker"
date: [creation date]
tags: [meta/tracker]
description: "문헌 읽기 진행 추적. Obsidian Bases에서 테이블/카드 뷰로 시각화."
---
```

### Paper Entry Format (in tracker body)

Each paper is a markdown table row:

```markdown
## Reading List

| # | Title | Phase | Status | Paper-1 Section | Priority | Takeaway | Date Read |
|---|-------|-------|--------|-----------------|----------|----------|-----------|
| 1 | R6 — PEML Spectrum | 1 | ⏳ | Ch.2 전체 | A | | |
| 2 | R1 — Hybrid Physics-Data | 1 | ⏳ | Ch.2 전체 | A | | |
| ...
```

Status values: `⏳ 대기` / `📖 읽는 중` / `✅ 읽음` / `⏭️ 건너뜀`

### Obsidian Base View: `99-meta/reading-tracker.base`

Create a .base file that references the tracker note for visual table view.

```json
{
  "type": "base",
  "source": {
    "type": "file",
    "path": "99-meta/reading-tracker.md"
  },
  "views": [{
    "type": "table",
    "name": "Reading Progress",
    "columns": ["#", "Title", "Phase", "Status", "Paper-1 Section", "Priority", "Takeaway"]
  }]
}
```

---

## Workflow

### `status` — Terminal Progress Report

1. Read `99-meta/reading-tracker.md`
2. Count by status: ✅/📖/⏳/⏭️
3. Count by phase
4. Report in Korean:

```
📚 문헌 읽기 진행 현황
━━━━━━━━━━━━━━━━━━━
전체: 23편
  ✅ 읽음: 3편 (13%)
  📖 읽는 중: 1편
  ⏳ 대기: 19편
  ⏭️ 건너뜀: 0편

Phase별:
  Phase 1 (Landscape): 1/3 완료
  Phase 2 (Paper-3): 0/4
  Phase 3 (Paper-1 Ch.2): 0/6
  Phase 4 (Metal Anchor): 0/4
  Phase 5 (보조): 0/6

다음 읽을 논문: R1 — Hybrid Physics-Data Fatigue (Phase 1, Priority A)
```

### `done <title>` — Mark as Read

1. Find the paper row in tracker
2. Update status to `✅ 읽음`
3. Set `Date Read` to today
4. Ask: "핵심 takeaway를 한 줄로 정리해 주세요 (Skip 가능):"
5. If answered, write to Takeaway column
6. Show next paper in queue

### `add-list <note-path>` — Bulk Import

1. Read the specified note
2. Find all table rows containing DOI/URL links
3. Extract: title, DOI/URL, suggested phase/priority/section
4. Append to reading-tracker.md
5. Report: "N편 추가 완료"

### `next` — Next Paper

1. Read tracker
2. Find first `⏳` paper by phase (1→2→3→4→5) then by priority (A→B→C)
3. Present:

```
📖 다음 읽을 논문:
  R1 — Hybrid Physics-Data Fatigue (Wang H et al., EFM 2023)
  Phase 1 | Priority A | Paper-1: Ch.2 전체
  DOI: 10.1016/j.engfracmech.2023.109242
  
  /paper-review R1 으로 리뷰를 시작하거나,
  /reading-tracker reading R1 으로 '읽는 중' 표시
```

---

## Initial Setup

When first invoked, if `99-meta/reading-tracker.md` does not exist:

1. Scan vault for literature list notes:
   - `(Resource) Paper-1 문헌 보강 2차 - Classical + Physics-AI Hybrid.md`
   - `(Resource) Paper-1 신규 레퍼런스 목록 (2026-03-30 팩트체크 완료).md`
2. Ask user which lists to import
3. Create tracker note + base file
4. Report initial status

## Terminal Report Language

All terminal output in Korean. Tracker note content uses mixed Korean + English (technical terms).
