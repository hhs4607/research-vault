---
name: paper-add
description: Resolve a DOI or paper title, fetch metadata, try to download a PDF, and add the paper to the local Zotero library. Use when the user wants a missing paper imported into Zotero from a DOI, title, or citation string.
---

# Paper Add

Use `scripts/paper_add.py` for the actual insertion and `../research-vault-harness/scripts/zotero_helper.py` to confirm that the paper appears afterward.

## Workflow

1. Parse the input:
   - DOI: pass through directly
   - title or citation: resolve DOI first with `scripts/paper_add.py --no-download`

2. Warn the user that Zotero desktop should be closed before DB writes. Do not write into the SQLite database while the app is open.

3. Run the helper script:

```bash
python3 scripts/paper_add.py --doi "10.1016/..."
python3 scripts/paper_add.py --title "paper title keywords" --author "LastName"
```

4. The script already handles:
   - Zotero directory detection
   - DOI lookup via Semantic Scholar
   - metadata lookup via CrossRef
   - open-access PDF lookup via Unpaywall
   - browser crawl fallback when Playwright is available
   - direct SQLite insertion and PDF attachment copy

5. After the script succeeds, verify with:

```bash
python3 ../research-vault-harness/scripts/zotero_helper.py search --query "title keywords" --limit 3
```

6. Report:
   - title
   - authors
   - journal and year
   - DOI
   - whether a PDF was attached
   - any manual recovery path if PDF download failed

7. Suggest `paper-review` or `paper-search` as the next step.

## Failure Handling

- If the DOI cannot be resolved, tell the user exactly which lookup failed.
- If Playwright is missing, keep the metadata-add path usable and report that PDF crawling was skipped.
- If the PDF cannot be found, leave the item in Zotero anyway and suggest manual acquisition routes.

## Script

- `scripts/paper_add.py`: imported from the existing vault workflow and kept as the deterministic Zotero-ingest path
