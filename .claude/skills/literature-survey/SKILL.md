---
name: literature-survey
description: "Conduct a multi-paper literature survey on a given research topic. Searches arxiv, Semantic Scholar, and web sources in parallel, then compiles a structured survey note with categorized findings, citation network analysis, and research gap identification. TRIGGER when: user asks for 'literature survey', 'survey papers on X', 'find related work', 'what's the state of the art in X', 'review the literature on X', 'research landscape', or needs a comprehensive overview of a research area."
---

# Literature Survey

Conduct a systematic literature survey and produce a structured vault note.

## Workflow

### Step 1: Define Scope

Clarify with user if not explicit:
- **Topic**: Primary research question or keywords
- **Scope**: Time range (default: last 5 years), paper count target (default: 15-20)
- **Focus areas**: Specific sub-topics or methods of interest
- **User's research context**: How this relates to their Paper-1~4 plan

### Step 2: Multi-Source Search (parallel)

Execute searches across multiple sources simultaneously:

1. **arxiv** (MCP): Search with topic keywords, filter by relevance
2. **Semantic Scholar** (MCP): Search for highly-cited papers, get citation counts
3. **Brave Search / Tavily** (MCP): Find survey papers, conference proceedings, recent preprints
4. Use **sequential-thinking** MCP to plan search strategy for complex topics

For each paper found, collect: title, authors, year, venue, citation count, abstract, DOI/URL.

### Step 3: Filter and Rank

Apply relevance criteria:
1. Direct relevance to user's research domains (fatigue, composites, PINN, DT, etc.)
2. Citation count and venue quality
3. Recency (prefer recent unless seminal work)
4. Methodological diversity (cover different approaches)

Target: top 15-20 papers from combined results.

### Step 4: Analyze and Categorize

Group papers by theme/method. Use sequential-thinking for categorization:
- **Category 1**: Methodology papers (the "how")
- **Category 2**: Application papers (the "where")
- **Category 3**: Review/survey papers (the "overview")
- **Category 4**: Foundational/seminal work (the "basis")

Identify: research trends, gaps, contradictions, and opportunities.

### Step 5: Generate Survey Note

Save to `01-inbox/(Survey) Topic Name — YYYY.md`:

```markdown
---
title: "Literature Survey — Topic Name"
date: YYYY-MM-DD
tags:
  - relevant/tags
  - from/taxonomy
description: "Literature survey on [topic] covering N papers from YYYY to YYYY"
source: "auto-generated survey"
---

# Literature Survey: Topic Name

## Overview
Brief summary of the research landscape (2-3 paragraphs).

## Paper Summary Table
| # | Authors (Year) | Title | Venue | Citations | Category | Key Contribution |
|---|---|---|---|---|---|---|

## Category Analysis

### Category 1: [Theme]
Narrative synthesis of papers in this category...

### Category 2: [Theme]
...

## Research Gaps and Opportunities
- Gap 1: ...
- Gap 2: ...

## Relevance to Current Research
How findings connect to user's Paper-1~4 plan and postdoc work.

## References
Full citation list in author-year format.
```

### Step 6: Update Tracking

- Add key papers to `99-meta/reading-tracker.md` with priority assessment
- Request vault-curator to file and tag the survey note

## Rules

- Always check existing vault notes first to avoid duplicating known papers
- Preserve user's existing review notes — reference them, don't recreate
- If fewer than 10 papers found, expand search terms and retry once
- Mark papers already in reading-tracker as "[already tracked]"
