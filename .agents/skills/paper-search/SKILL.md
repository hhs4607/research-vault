---
name: paper-search
description: Search the local Zotero library by title, author, journal, collection, tag, or DOI fragment and return a brief Korean briefing. Use when the user asks whether a paper is already in Zotero, wants the PDF path for a known paper, wants candidate papers on a topic, or wants a quick shortlist before a deeper review.
---

# Paper Search

Read `../research-vault-harness/references/vault-conventions.md` if the request may lead to a saved note. Use `../research-vault-harness/scripts/zotero_helper.py` for the actual lookup.

## Workflow

1. Search the library:

```bash
python3 ../research-vault-harness/scripts/zotero_helper.py search --query "search terms" --limit 8
```

2. Deduplicate and rank:
   - prefer title matches over loose metadata matches
   - prefer entries with PDF attachments
   - keep the first response to at most 5 papers unless the user asks for more

3. For each returned paper, show:
   - title
   - authors
   - year
   - journal
   - collections
   - whether a PDF exists
   - a short Korean summary based on the abstract when available

4. If the user needs the actual file path, fetch the selected item:

```bash
python3 ../research-vault-harness/scripts/zotero_helper.py item --item-id 1491
```

5. If nothing matches, suggest:
   - shorter title keywords
   - first author surname
   - DOI fragment
   - `paper-add` if the paper is likely missing from Zotero

## Output Shape

- If there is one clear match, brief it directly.
- If there are multiple matches, number them and ask the user which one to open or review.
- End with the most useful next action:
  - `paper-review` for deep discussion
  - `paper-add` if the paper is missing
  - direct PDF path if the user only needed the attachment

## Notes

- Keep the user-facing summary in Korean unless the user asks otherwise.
- Use absolute PDF paths when reporting attachment files.
