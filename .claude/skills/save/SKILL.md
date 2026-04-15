---
name: save
description: "Save content (YouTube URL, web URL, or raw text) to Obsidian vault. Extracts content, translates to Korean if needed, generates frontmatter, saves to 01-inbox, and suggests related notes."
---

# Save Content to Obsidian

Save any content (YouTube, web page, or text) to Obsidian vault.

## Prerequisites

All `obsidian` CLI commands require Obsidian to be running. PATH must include `/Applications/Obsidian.app/Contents/MacOS`.

## Workflow

### Step 1: Detect Input Type
- YouTube URL (contains youtube.com or youtu.be) → YouTube extraction
- Web URL (starts with http:// or https://) → Web extraction
- Everything else → Raw text

### Step 2: Extract Content

**YouTube:**
1. Get video title: yt-dlp --print "%(title)s" "<URL>"
2. Get channel name: yt-dlp --print "%(channel)s" "<URL>"
3. Download subtitles: yt-dlp --write-sub --write-auto-sub --sub-lang "ko,en" --sub-format "vtt" --skip-download -o "/tmp/yt-sub" "<URL>"
4. Clean VTT to plain text (remove timestamps, merge duplicate lines)
5. Restructure into readable prose with section headings

**Web Page:**
Use WebFetch tool to extract the page content as markdown.

**Raw Text:**
Use the input text as-is.

### Step 3: Translate
If content is not Korean, translate to Korean.

### Step 4: Generate Frontmatter
- title: descriptive title in content language
- date: today (YYYY-MM-DD)
- tags: 3-6 tags from `99-meta/tag-taxonomy.md` (read taxonomy first, select matching tags; if no suitable tag exists, propose new tag to user → add to taxonomy before use)
  - Use `obsidian tags counts sort=count` to see current tag usage for context
- aliases: 2-3 search-friendly alternative names
- description: 1-2 sentence Korean summary
- source: original URL (if applicable)
- author: channel/author name (if applicable)

Filename: English kebab-case, max 50 chars (e.g. react-hooks-guide.md)

### Step 5: Save
Create note using CLI for immediate Obsidian index registration:
```bash
obsidian create path="01-inbox/filename.md" content="---\ntitle: ...\n---\n\nBody content" silent
```
If content is too long for CLI argument, use `Write` tool to create the file, then verify with `obsidian read path="01-inbox/filename.md"`.

### Step 6: Related Notes
Search vault for related notes using CLI:
```bash
obsidian search query="keyword" limit=10
obsidian backlinks file="filename"
```
Suggest 2-5 related notes with relationship type.
Let user pick which to link. Append as "## Related Content to Explore" with [[wikilinks]].

### Step 7: Capture Thoughts
Ask user for personal reaction with 2-3 content-specific prompts + "Skip".
If answered, append as "## 내 생각" section (1-3 bullet points).

### Step 8: Next Action
Offer: Deep-dive (내용 탐구) / Organize (폴더 정리) / Done
