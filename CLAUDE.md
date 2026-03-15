# Obsidian Vault Instructions

## Vault Structure (PARA)

This vault uses the PARA method:
- 01-inbox/: Unsorted notes — default location for all new notes
- 02-daily-notes/: Daily journal entries (YYYY/MM/YYYY-MM-DD-topic.md)
- 03-projects/: Active projects (time-bounded)
- 04-areas/: Ongoing domains & concepts (open-ended)
- 05-resources/: Reference materials (papers, tools, datasets)
- 06-archives/: Completed projects
- 99-meta/: Templates and attachments

## Note Format (Frontmatter)

All .md files must include frontmatter:

```yaml
---
title: "Note Title"
date: 2024-07-27
tags: [category/subcategory]
description: "Core content summary (1-2 sentences in Korean)"
source: "https://..."   # only when saved from URL
---
```

- File name: `(Category) Readable Title.md` format (e.g., `(Research) Paper-3 PINN Fatigue Degradation.md`)
- Title: English for technical terms, Korean for proper nouns (e.g., `(Research) 포닥 논문 계획.md`)
- Daily note file name: `YYYY-MM-DD-topic.md` (e.g., `2026-03-14-pinn-prototype.md`)
- Categories: Research / Idea / Study / Paper / Resource / Concept / Meeting
- Tag format: category/subcategory (e.g., ai/pinn, research/fatigue)

## Tag System

- **Taxonomy file**: `99-meta/tag-taxonomy.md` — single source of truth for all allowed tags
- All tags must exist in taxonomy before use in any note
- When assigning tags, read taxonomy first and select 3-6 matching tags
- If no suitable tag exists, propose new tag → add to taxonomy → then apply
- Use `/tag` skill to manage taxonomy (add, merge, rename, audit)

## Validation

When creating notes:
- title, date, tags are required
- File names must follow `(Category) Title.md` format for organized notes
- [[wikilinks]] must point to existing files only

## MOC (Map of Contents)

- Each PARA folder has a MOC.md file
- When moving notes with /organize, update BOTH source MOC (remove) and target MOC (add)
- When creating a new folder, create MOC.md as well

## Conversation Behavior

- When I ask a question, search the vault for related notes before answering
- For requests like "do I have notes on this?", always search the vault first
- For general knowledge questions, answer directly without searching

## Content Workflow

- Save request → run /save skill
- Deep-dive request → run /deep-dive skill
- Organize request → run /organize skill

## Plan Mode

Before working across multiple files:
- Summarize the plan concisely and show it to the user
- Execute only after user confirmation

## Related Note Linking (optional)

When saving or organizing notes, suggest 2-5 related notes from the vault to link.
The value of this feature grows as the vault accumulates notes.
