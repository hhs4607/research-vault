## `zotero_helper.py`

Shared helper for local Zotero operations. Use this before writing raw SQL.

Path:

`../scripts/zotero_helper.py`

## Commands

### Locate the Zotero data directory

```bash
python3 ../scripts/zotero_helper.py locate
```

Returns JSON with `zotero_dir` and `db_path`.

### Search the library

```bash
python3 ../scripts/zotero_helper.py search --query "transformer fatigue" --limit 8
```

Searches title, authors, collections, tags, DOI, and journal fields. Returns JSON records with:

- `item_id`
- `key`
- `item_type`
- `title`
- `authors`
- `date`
- `year`
- `journal`
- `doi`
- `url`
- `collections`
- `tags`
- `abstract`
- `attachment_count`

### Fetch one item

```bash
python3 ../scripts/zotero_helper.py item --item-id 1491
python3 ../scripts/zotero_helper.py item --key 99D2BPVY
```

Returns full JSON metadata plus resolved attachment paths in `attachments`.

## PDF handling

- Use the first `application/pdf` attachment path when present
- Inspect with `pdfinfo`
- Extract readable text with `pdftotext <pdf> -`

## WSL behavior

- The helper auto-detects the Windows Zotero data directory when running inside WSL
- If detection fails, pass `ZOTERO_DIR=/path/to/Zotero` in the environment
