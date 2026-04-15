---
name: paper-search
description: Search Zotero library by title, author, collection, or tag with brief summary
argument-hint: [search term]
---

# Paper Search — Quick Zotero Lookup + Brief Summary

Search the Zotero library and present a brief summary for each result.

**Input:** $ARGUMENTS (search term — title keywords, author name, collection name, or tag)

## Step 1: Locate Zotero Data Directory

Detect the Zotero data directory automatically based on the OS:

```bash
OS="$(uname -s)"
case "$OS" in
  Linux*)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      WIN_USER=$(cmd.exe /C "echo %USERNAME%" 2>/dev/null | tr -d '\r')
      ZOTERO_DIR="/mnt/c/Users/${WIN_USER}/Zotero"
    else
      ZOTERO_DIR="$HOME/Zotero"
    fi
    ;;
  Darwin*)
    ZOTERO_DIR="$HOME/Zotero"
    ;;
esac
```

If the directory is not found, search for `zotero.sqlite` to locate it.

## Step 2: Search Across Multiple Fields

Run searches in parallel across title, author, collection, and tags:

```sql
-- Title match
SELECT 'title' AS match_type, i.itemID, i.key, idv.value AS title
FROM items i
JOIN itemData id ON i.itemID = id.itemID
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'title'
JOIN itemDataValues idv ON id.valueID = idv.valueID
WHERE idv.value LIKE '%SEARCH_TERM%'
AND i.itemTypeID NOT IN (14, 1)

UNION

-- Author match
SELECT 'author' AS match_type, i.itemID, i.key, idv.value AS title
FROM items i
JOIN itemCreators ic ON i.itemID = ic.itemID
JOIN creators c ON ic.creatorID = c.creatorID
JOIN itemData id ON i.itemID = id.itemID
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'title'
JOIN itemDataValues idv ON id.valueID = idv.valueID
WHERE (c.lastName LIKE '%SEARCH_TERM%' OR c.firstName LIKE '%SEARCH_TERM%')
AND i.itemTypeID NOT IN (14, 1)

UNION

-- Collection match
SELECT 'collection' AS match_type, i.itemID, i.key, idv.value AS title
FROM items i
JOIN collectionItems ci ON i.itemID = ci.itemID
JOIN collections col ON ci.collectionID = col.collectionID
JOIN itemData id ON i.itemID = id.itemID
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'title'
JOIN itemDataValues idv ON id.valueID = idv.valueID
WHERE col.collectionName LIKE '%SEARCH_TERM%'
AND i.itemTypeID NOT IN (14, 1)

UNION

-- Tag match
SELECT 'tag' AS match_type, i.itemID, i.key, idv.value AS title
FROM items i
JOIN itemTags it ON i.itemID = it.itemID
JOIN tags t ON it.tagID = t.tagID
JOIN itemData id ON i.itemID = id.itemID
JOIN fields f ON id.fieldID = f.fieldID AND f.fieldName = 'title'
JOIN itemDataValues idv ON id.valueID = idv.valueID
WHERE t.name LIKE '%SEARCH_TERM%'
AND i.itemTypeID NOT IN (14, 1);
```

## Step 3: Enrich Results with Metadata + Abstract

For each unique result (deduplicated by itemID), fetch:
- Authors (firstName, lastName)
- Year (from the `date` field)
- Journal/publication name
- Abstract (from the `abstractNote` field)
- Collections it belongs to
- Whether a PDF attachment exists

## Step 4: Present Results with Brief Summary

For each paper found, present:

```
## Zotero Search: "[search term]"

Found [N] papers:

### 1. [Paper Title]
**Authors:** [list] | **Year:** [year] | **Journal:** [journal]
**Collections:** [list] | **PDF:** yes/no

**Brief Summary:** [2-3 sentence summary based on the abstract — what the paper does, how, and key finding. Written in Korean for quick scanning.]

---

### 2. [Next Paper Title]
...

To start a deep review discussion: `/paper-review [title or author]`
```

If only 1 result is found, present the brief summary directly without numbering.

If no results found, suggest alternative search terms or list available collections.
