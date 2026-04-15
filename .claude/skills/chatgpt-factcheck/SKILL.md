---
name: chatgpt-factcheck
description: "Crawl a ChatGPT shared conversation link, extract all claims and source URLs, fact-check each source, analyze relevance to a specified paper (default: Paper-1), and save verified results as an Obsidian note."
---

# ChatGPT Fact-Check & Research Integration

Crawl a ChatGPT shared conversation, verify all claims against their sources, analyze relevance to the user's research papers, and save as a structured Obsidian note.

## Trigger

- User provides a ChatGPT shared link (`chatgpt.com/share/...`)
- User asks to fact-check ChatGPT output
- User asks to verify and organize ChatGPT research findings

## Input

- **Required**: ChatGPT shared URL (`https://chatgpt.com/share/...`)
- **Optional**: Target paper for relevance analysis (default: `Paper-1`)
  - Accepts: `Paper-1`, `Paper-2`, `Paper-3`, `Paper-4`, or any note name/path

## Output Language Policy

- **Skill file (this file)**: English — for AI consumption
- **Obsidian notes**: Korean body text with English technical terms in parentheses
- **Terminal reports**: Korean — user-facing progress updates
- **Frontmatter title**: Korean + English mixed OK
- **Tags, DOI, author names**: Keep original language

## Workflow

### Step 1: Crawl ChatGPT Conversation

Use Playwright to render the JavaScript-heavy ChatGPT shared page and extract content.

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(8000)

    # Extract conversation text
    full_text = page.inner_text('body')

    # Extract all source URLs (citations are in small badge-like <a> elements)
    links = page.eval_on_selector_all('a[href]',
        'els => els.map(e => ({text: e.innerText.trim(), href: e.href, class: e.className}))')

    # Filter for academic/data sources (exclude chatgpt.com, openai.com UI links)
    source_links = [l for l in links
        if l['href'] and 'chatgpt.com' not in l['href'] and 'openai.com' not in l['href']
        and any(domain in l['href'] for domain in [
            'zenodo', 'pubmed', 'sciencedirect', 'doi.org', 'arxiv',
            'springer', 'wiley', 'mdpi', 'nature', 'ieee', 'scopus',
            'github', 'nasa', 'nrel', 'nih.gov'
        ])]

    browser.close()
```

**Fallback**: If Playwright fails, ask user to paste conversation text directly.

### Step 2: Extract Claims

From the conversation text, identify all **verifiable factual claims**:

- Dataset descriptions (size, format, license, content)
- Paper/publication references (title, authors, journal, year)
- Numerical claims (frequencies, pressures, measurements)
- Institutional attributions (who released what)
- URLs and DOIs

Create a structured claim list:

```
Claim #1: [claim text]
Source cited: [URL or "none"]
Category: dataset / publication / numerical / institutional
```

### Step 3: Fact-Check Each Source

Visit each extracted URL to verify against the original source.

**Strategy by domain:**

| Domain | Method | What to verify |
|--------|--------|----------------|
| Zenodo | Playwright or WebFetch | Record exists, title matches, license, size, authors |
| PubMed | WebFetch (Playwright gets 403) | PMID exists, title/authors/journal match, DOI |
| ScienceDirect | WebFetch (Playwright often blocked) | Article exists, DOI matches, content aligns |
| DOI.org | WebFetch `https://doi.org/[DOI]` | Resolves to actual paper |
| arXiv | WebFetch | Paper exists, title/authors match |
| GitHub | `gh` CLI or WebFetch | Repo exists, description matches |

**Verdict categories:**
- ✅ **Confirmed** — Source directly supports the claim
- ⚠️ **Partial** — Source exists but claim is exaggerated or slightly inaccurate
- ❌ **Not found** — URL is dead, or source does not support the claim
- 🔍 **Unverifiable** — No source cited, cannot independently confirm

### Step 4: Analyze Paper Relevance

Read the target paper note from the vault to understand its structure and research gaps.

**Default target**: `03-projects/(Research) Paper-1 Review Multiscale Fatigue AI DT.md`

**Relevance mapping process:**

1. Read the target paper note (frontmatter, chapter structure, key themes)
2. For each verified finding, check:
   - Which chapter/section does it relate to?
   - Does it fill a gap (missing reference, dataset, validation)?
   - Usage type: benchmark data / literature reference / method comparison / validation target
3. Also check Paper-2, Paper-3, Paper-4 relevance if connection is strong

### Step 5: Generate Obsidian Note

Save to `01-inbox/` following vault conventions. **Write note body in Korean** with English technical terms in parentheses.

**Filename**: `(Resource) [Descriptive Title].md`

**Frontmatter template:**

```yaml
---
title: "[Korean + English mixed title]"
date: [today's date]
tags: [select 3-6 from tag-taxonomy.md, add new tags if needed]
description: "[1-2 sentence Korean summary]"
source: "[primary URL from the ChatGPT conversation]"
---
```

**Note structure (all in Korean):**

```markdown
# [Title]

## 개요
[Brief description — Korean]

## 데이터셋/리소스 구성
[Detailed breakdown — tables preferred]

## 저자 / 기관
[Creator info]

## 관련 논문
[DOIs, PMIDs, journal names — verified only]

## 팩트체크 결과
| ChatGPT 주장 | 검증 | 비고 |
|-------------|------|------|
| ... | ✅/⚠️/❌/🔍 | ... |

## Paper-1 연관성 분석
[Chapter-by-chapter mapping — Korean]

### Paper-2~4 잠재적 활용
[Table format]
```

### Step 6: Suggest Related Notes

Search the vault for potentially related notes by tags and keywords. Suggest 2-5 notes for `[[wikilinks]]`.

### Step 7: Tag Maintenance

If new tags are needed:
1. Add to `99-meta/tag-taxonomy.md` first
2. Then apply to the new note

## Terminal Report Format

Report progress in Korean at each step:

```
[Step 1] 크롤링 완료 — 출처 N개 추출
[Step 2] 주장 N개 식별
[Step 3] 팩트체크 결과: ✅ N개 / ⚠️ N개 / ❌ N개
[Step 4] Paper-1 연관 섹션: Ch.X.Y, Ch.X.Y, ...
[Step 5] 노트 저장 완료 — 01-inbox/(Resource) 제목.md
[Step 6] 관련 노트 N개 추천
```

## Error Handling

- **Playwright not installed**: `pip install playwright && playwright install chromium`
- **ChatGPT page won't render**: Ask user to paste conversation text
- **Source URL blocked (403/captcha)**: Try WebFetch as fallback, note as "access restricted" in fact-check
- **PubMed blocks Playwright**: Always use WebFetch for PubMed
- **ScienceDirect blocks both**: Cross-reference via DOI on PubMed or doi.org

## Step 8: Post-Actions

After note is saved, suggest follow-up actions based on what was found:

### 8-1. Zotero Integration
For each ✅ confirmed source with DOI:
- Suggest: "확인된 논문 N편을 Zotero에 추가할까요? → /paper-add [DOI]"
- List the confirmed DOIs for easy copy

### 8-2. Reading Tracker
If `99-meta/reading-tracker.md` exists:
- Suggest: "검증된 N편을 reading tracker에 추가할까요? → /reading-tracker add-list [note-path]"

### 8-3. Deep Review
For the most relevant confirmed paper:
- Suggest: "가장 관련성 높은 [paper name]을 상세 리뷰할까요? → /paper-review [DOI]"

### 8-4. Organize
- Suggest: "/organize 로 PARA 폴더에 분류할까요?"

---

## Examples

**Basic usage:**
```
User: https://chatgpt.com/share/abc123 탐색 실시
→ Crawl → Extract → Fact-check → Map to Paper-1 → Save note (Korean)
```

**With specific paper target:**
```
User: https://chatgpt.com/share/abc123 Paper-3 관련 정리
→ Crawl → Extract → Fact-check → Map to Paper-3 → Save note (Korean)
```

**Multiple links:**
```
User: [link1] [link2] [link3] 전부 정리해줘
→ Process each link in parallel, save separate notes (Korean)
```
