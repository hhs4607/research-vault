---
name: deep-dive
description: "Deep-dive into a note to explore concepts, unpack claims, and compile insights. Uses Sequential Thinking MCP for structured analysis. Appends findings as a Deep Dive section to the original note."
---

# Deep-Dive Note

Discuss an article to deepen understanding, then compile into a deep-dive note.
Uses Sequential Thinking MCP for structured analysis before each interaction.

## Prerequisites

All `obsidian` CLI commands require Obsidian to be running. PATH must include `/Applications/Obsidian.app/Contents/MacOS`.

## Workflow

### Step 1: Read & Analyze with Sequential Thinking
Read the note: `obsidian read path="..."` or `obsidian read file="Note Title"`.
Check existing connections: `obsidian backlinks file="Note Title"`.
Then use `mcp__sequential-thinking__sequentialthinking` to:
- Identify main ideas and concepts worth exploring
- Analyze gaps, implicit assumptions, and hidden depth
- Generate 2-4 exploration topics ranked by depth potential
- Consider connections to other notes in the vault

### Step 2: Present Topics
Surface 2-4 things worth exploring (from ST analysis). Don't summarize the article. Identify:
- Concepts with hidden depth
- Claims worth unpacking
- Implicit assumptions
- Connections to existing vault knowledge

Ask: "What catches your interest?"

### Step 3: Discuss (ST-powered follow-up)
Role: explainer and discussion partner (NOT interviewer).

After each user response, use Sequential Thinking to:
- Analyze what the user said for new insights, unstated implications, and follow-up angles
- Determine if the response opens a deeper thread worth pursuing
- Generate a follow-up question or explanation that builds on the user's specific input

Discussion guidelines:
- Explain with analogies and concrete examples
- Use markdown tables to compare/contrast
- Search the web if needed for better answers
- Follow the thread — let the user's answers guide the next question (chain of thought)
- When ST determines the topic is sufficiently explored (or user says "정리해줘" / "compile") → go to Step 4

### Step 4: Compile
CRITICAL: Preserve FULL explanations. Do NOT summarize.
- ### numbered heading per topic explored
- Include all analogies, examples, tables from discussion
- End with ### Key Insight (blockquote summary)

### Step 5: Append
Append the Deep Dive section to the original note:
```bash
obsidian append path="folder/note.md" content="\n## Deep Dive (2026-03-15)\n\n### 1. Topic...\n..."
```
For long content, use `Edit` tool to append, then verify with `obsidian read path="..."`.

### Step 6: Update Tags
1. Get current tags: `obsidian tags path="folder/note.md"`
2. Get vault tag stats: `obsidian tags counts sort=count`
3. Read `99-meta/tag-taxonomy.md` for reference
4. Check if deep-dive topics introduced concepts covered by existing tags
5. Update tags: `obsidian property:set name="tags" value="[tag1, tag2, ...]" path="..."`
6. If a new concept has no matching tag, propose new tag to user → add to taxonomy first
7. Keep total tags per note at 3-6

### Step 7: Capture Thoughts
Ask for personal reaction with content-specific prompts + "Skip".
If answered, append as "## 내 생각" section.
