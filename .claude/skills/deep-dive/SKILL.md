---
name: deep-dive
description: "Deep-dive into a note to explore concepts, unpack claims, and compile insights. Interactive discussion with user — never auto-append. Appends findings only after user confirmation."
---

# Deep-Dive Note

Discuss an article to deepen understanding, then compile into a deep-dive note.
**CRITICAL: This is an INTERACTIVE skill. Never auto-generate and append. Always discuss with the user first.**

## Prerequisites

Obsidian CLI is optional — use Read/Grep tools as fallback if Obsidian is not running.

## Workflow

### Step 1: Read & Analyze (silent)

Read the note using Read tool (preferred) or `obsidian read`.
Check existing connections: search vault with Grep for related terms / wikilinks.

**Analysis method (choose based on availability):**

**Option A — Sequential Thinking MCP available:**
Use `mcp__sequential-thinking__sequentialthinking` to:
- Identify main ideas and concepts worth exploring
- Analyze gaps, implicit assumptions, and hidden depth
- Generate 2-4 exploration topics ranked by depth potential
- Consider connections to other notes in the vault

**Option B — Sequential Thinking MCP unavailable (fallback):**
Perform structured analysis directly:
1. Read the note fully
2. Search vault for related notes (Grep by key terms, tags)
3. Identify 2-4 exploration topics by:
   - Scanning for claims without evidence or TBD markers
   - Finding concepts mentioned but not explained
   - Detecting implicit assumptions in the argument
   - Checking connections to other vault notes (especially Paper-1~4)
4. Rank topics by depth potential and relevance to user's research

### Step 2: Present Brief + Topics

**First**, give a concise briefing of the document:
- 문서 성격 (1줄)
- 핵심 내용 요약 (테이블 또는 3-5 bullet)
- 현재 완성도 평가

**Then**, surface 2-4 things worth exploring deeper. Don't dump analysis — present options:
- Concepts with hidden depth
- Claims worth unpacking
- Implicit assumptions
- Connections to existing vault knowledge

**Ask**: "어떤 부분이 궁금하세요?" or "어디부터 파볼까요?"

**WAIT for user response. Do NOT proceed without input.**

### Step 3: Discuss (interactive, multi-turn)

Role: explainer and discussion partner (NOT interviewer, NOT auto-generator).

**Rules:**
- ONE topic at a time. Go deep, not wide.
- After each user response, analyze (using ST if available, or direct reasoning):
  - What the user said for new insights, unstated implications, and follow-up angles
  - Whether the response opens a deeper thread worth pursuing
  - A follow-up question or explanation that builds on the user's specific input
- Present findings and ask for user's opinion before moving on
- Use markdown tables to compare/contrast when useful
- Search the web if needed for better answers
- Follow the thread — let the user's answers guide the next question
- When topic is sufficiently explored, ask: "이 내용 노트에 추가할까요?" or "다음 토픽으로 넘어갈까요?"

**Discussion flow per topic:**
```
Claude: [토픽 제시 + 분석 + 질문]
  ↓
User: [의견/질문/추가 정보]
  ↓
Claude: [응답 + 더 깊은 분석 + follow-up]
  ↓
... (반복) ...
  ↓
Claude: "이 내용 정리해서 노트에 추가할까요?"
User: "응" / "좀 더 다듬어줘" / "다음 토픽으로"
```

**NEVER skip discussion. NEVER auto-append without explicit user approval.**

### Step 4: Compile (per topic, with confirmation)

When user agrees to add content:
- PRESERVE full explanations from discussion — do NOT over-summarize
- ### numbered heading per topic explored
- Include all analogies, examples, tables from discussion
- **Show the compiled section to user first** before appending
- Ask: "이대로 추가할까요?"

### Step 5: Append (only after user says yes)

Append the confirmed Deep Dive section to the original note:
```bash
obsidian append path="folder/note.md" content="\n## Deep Dive (2026-04-04)\n\n### 1. Topic...\n..."
```
For long content, use `Edit` tool to append, then verify with `obsidian read path="..."`.

If multiple topics were discussed across turns, append incrementally or compile at the end — follow user's preference.

### Step 6: Update Tags

1. Get current tags: `obsidian tags path="folder/note.md"`
2. Read `99-meta/tag-taxonomy.md` for reference
3. Check if deep-dive topics introduced concepts covered by existing tags
4. Propose tag changes to user — don't auto-apply
5. Keep total tags per note at 3-6

### Step 7: Capture Thoughts

Ask for personal reaction with content-specific prompts + "Skip".
If answered, append as "## 내 생각" section.

## Batch Mode (agent-driven)

When deep-dive is called by an Agent (not directly by user), the interactive steps (2-3) are skipped and full analysis is auto-appended. This is the ONLY exception to the interactive rule.

Mark batch-generated sections with: `## Deep Dive (날짜) — auto-generated`
so the user knows these were not interactively reviewed.
