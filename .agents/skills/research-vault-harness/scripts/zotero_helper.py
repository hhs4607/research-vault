#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def detect_zotero_dir() -> Path | None:
    override = os.environ.get("ZOTERO_DIR")
    if override:
        candidate = Path(override).expanduser()
        if (candidate / "zotero.sqlite").exists():
            return candidate

    candidates = []
    home = Path.home()

    # Native Linux/macOS convention.
    candidates.append(home / "Zotero")

    # WSL convention.
    try:
        version = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
        if "microsoft" in version:
            result = subprocess.run(
                ["cmd.exe", "/C", "echo %USERNAME%"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            win_user = result.stdout.strip().replace("\r", "")
            if win_user:
                candidates.append(Path("/mnt/c/Users") / win_user / "Zotero")
    except OSError:
        pass

    for candidate in candidates:
        if (candidate / "zotero.sqlite").exists():
            return candidate

    search_roots = [home, Path("/mnt/c/Users")]
    for root in search_roots:
        if not root.exists():
            continue
        try:
            for db_path in root.glob("**/zotero.sqlite"):
                return db_path.parent
        except OSError:
            continue
    return None


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


SEARCH_SQL = """
WITH title_data AS (
    SELECT itemData.itemID, itemDataValues.value AS title
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'title'
),
date_data AS (
    SELECT itemData.itemID, itemDataValues.value AS date_value
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'date'
),
journal_data AS (
    SELECT itemData.itemID, itemDataValues.value AS journal
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'publicationTitle'
),
doi_data AS (
    SELECT itemData.itemID, itemDataValues.value AS doi
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'DOI'
),
url_data AS (
    SELECT itemData.itemID, itemDataValues.value AS url
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'url'
),
abstract_data AS (
    SELECT itemData.itemID, itemDataValues.value AS abstract_note
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'abstractNote'
),
author_data AS (
    SELECT
        itemCreators.itemID,
        GROUP_CONCAT(
            creators.lastName ||
            CASE
                WHEN creators.firstName IS NOT NULL AND creators.firstName != ''
                THEN ', ' || creators.firstName
                ELSE ''
            END,
            ' | '
        ) AS authors
    FROM itemCreators
    JOIN creators USING (creatorID)
    JOIN creatorTypes USING (creatorTypeID)
    WHERE creatorTypes.creatorType = 'author'
    GROUP BY itemCreators.itemID
),
collection_data AS (
    SELECT
        collectionItems.itemID,
        GROUP_CONCAT(collections.collectionName, ' | ') AS collections
    FROM collectionItems
    JOIN collections USING (collectionID)
    GROUP BY collectionItems.itemID
),
tag_data AS (
    SELECT
        itemTags.itemID,
        GROUP_CONCAT(tags.name, ' | ') AS tags
    FROM itemTags
    JOIN tags USING (tagID)
    GROUP BY itemTags.itemID
),
attachment_data AS (
    SELECT
        parentItemID AS itemID,
        COUNT(*) AS attachment_count
    FROM itemAttachments
    GROUP BY parentItemID
)
SELECT
    items.itemID,
    items.key,
    itemTypes.typeName AS item_type,
    title_data.title,
    COALESCE(author_data.authors, '') AS authors,
    COALESCE(date_data.date_value, '') AS date_value,
    COALESCE(journal_data.journal, '') AS journal,
    COALESCE(doi_data.doi, '') AS doi,
    COALESCE(url_data.url, '') AS url,
    COALESCE(collection_data.collections, '') AS collections,
    COALESCE(tag_data.tags, '') AS tags,
    COALESCE(abstract_data.abstract_note, '') AS abstract_note,
    COALESCE(attachment_data.attachment_count, 0) AS attachment_count
FROM items
JOIN itemTypes USING (itemTypeID)
JOIN title_data ON title_data.itemID = items.itemID
LEFT JOIN author_data ON author_data.itemID = items.itemID
LEFT JOIN date_data ON date_data.itemID = items.itemID
LEFT JOIN journal_data ON journal_data.itemID = items.itemID
LEFT JOIN doi_data ON doi_data.itemID = items.itemID
LEFT JOIN url_data ON url_data.itemID = items.itemID
LEFT JOIN collection_data ON collection_data.itemID = items.itemID
LEFT JOIN tag_data ON tag_data.itemID = items.itemID
LEFT JOIN abstract_data ON abstract_data.itemID = items.itemID
LEFT JOIN attachment_data ON attachment_data.itemID = items.itemID
WHERE itemTypes.typeName NOT IN ('attachment', 'note', 'annotation')
  AND (
      LOWER(title_data.title) LIKE :pattern
      OR LOWER(COALESCE(author_data.authors, '')) LIKE :pattern
      OR LOWER(COALESCE(collection_data.collections, '')) LIKE :pattern
      OR LOWER(COALESCE(tag_data.tags, '')) LIKE :pattern
      OR LOWER(COALESCE(doi_data.doi, '')) LIKE :pattern
      OR LOWER(COALESCE(journal_data.journal, '')) LIKE :pattern
  )
ORDER BY attachment_count DESC, title_data.title ASC
LIMIT :limit;
"""


ITEM_SQL = """
WITH title_data AS (
    SELECT itemData.itemID, itemDataValues.value AS title
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'title'
),
date_data AS (
    SELECT itemData.itemID, itemDataValues.value AS date_value
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'date'
),
journal_data AS (
    SELECT itemData.itemID, itemDataValues.value AS journal
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'publicationTitle'
),
doi_data AS (
    SELECT itemData.itemID, itemDataValues.value AS doi
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'DOI'
),
url_data AS (
    SELECT itemData.itemID, itemDataValues.value AS url
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'url'
),
abstract_data AS (
    SELECT itemData.itemID, itemDataValues.value AS abstract_note
    FROM itemData
    JOIN fieldsCombined USING (fieldID)
    JOIN itemDataValues USING (valueID)
    WHERE fieldsCombined.fieldName = 'abstractNote'
),
author_data AS (
    SELECT
        itemCreators.itemID,
        GROUP_CONCAT(
            creators.lastName ||
            CASE
                WHEN creators.firstName IS NOT NULL AND creators.firstName != ''
                THEN ', ' || creators.firstName
                ELSE ''
            END,
            ' | '
        ) AS authors
    FROM itemCreators
    JOIN creators USING (creatorID)
    JOIN creatorTypes USING (creatorTypeID)
    WHERE creatorTypes.creatorType = 'author'
    GROUP BY itemCreators.itemID
),
collection_data AS (
    SELECT
        collectionItems.itemID,
        GROUP_CONCAT(collections.collectionName, ' | ') AS collections
    FROM collectionItems
    JOIN collections USING (collectionID)
    GROUP BY collectionItems.itemID
),
tag_data AS (
    SELECT
        itemTags.itemID,
        GROUP_CONCAT(tags.name, ' | ') AS tags
    FROM itemTags
    JOIN tags USING (tagID)
    GROUP BY itemTags.itemID
),
attachment_data AS (
    SELECT
        parentItemID AS itemID,
        COUNT(*) AS attachment_count
    FROM itemAttachments
    GROUP BY parentItemID
)
SELECT
    items.itemID,
    items.key,
    itemTypes.typeName AS item_type,
    COALESCE(title_data.title, '') AS title,
    COALESCE(author_data.authors, '') AS authors,
    COALESCE(date_data.date_value, '') AS date_value,
    COALESCE(journal_data.journal, '') AS journal,
    COALESCE(doi_data.doi, '') AS doi,
    COALESCE(url_data.url, '') AS url,
    COALESCE(collection_data.collections, '') AS collections,
    COALESCE(tag_data.tags, '') AS tags,
    COALESCE(abstract_data.abstract_note, '') AS abstract_note,
    COALESCE(attachment_data.attachment_count, 0) AS attachment_count
FROM items
JOIN itemTypes USING (itemTypeID)
LEFT JOIN title_data ON title_data.itemID = items.itemID
LEFT JOIN author_data ON author_data.itemID = items.itemID
LEFT JOIN date_data ON date_data.itemID = items.itemID
LEFT JOIN journal_data ON journal_data.itemID = items.itemID
LEFT JOIN doi_data ON doi_data.itemID = items.itemID
LEFT JOIN url_data ON url_data.itemID = items.itemID
LEFT JOIN collection_data ON collection_data.itemID = items.itemID
LEFT JOIN tag_data ON tag_data.itemID = items.itemID
LEFT JOIN abstract_data ON abstract_data.itemID = items.itemID
LEFT JOIN attachment_data ON attachment_data.itemID = items.itemID
WHERE itemTypes.typeName NOT IN ('attachment', 'note', 'annotation')
  AND (
      (:item_id IS NOT NULL AND items.itemID = :item_id)
      OR (:item_key IS NOT NULL AND items.key = :item_key)
  )
LIMIT 1;
"""


def split_pipe(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def year_from_date(date_value: str) -> str:
    for char_index in range(len(date_value) - 3):
        snippet = date_value[char_index:char_index + 4]
        if snippet.isdigit():
            return snippet
    return ""


def resolve_storage_path(zotero_dir: Path, attachment_key: str, raw_path: str) -> str:
    if raw_path.startswith("storage:"):
        relative_name = raw_path.split("storage:", 1)[1]
        return str(zotero_dir / "storage" / attachment_key / relative_name)
    return raw_path


def normalize_row(row: sqlite3.Row) -> dict:
    data = dict(row)
    return {
        "item_id": data["itemID"],
        "key": data["key"],
        "item_type": data["item_type"],
        "title": data["title"],
        "authors": split_pipe(data["authors"]),
        "date": data["date_value"],
        "year": year_from_date(data["date_value"]),
        "journal": data["journal"],
        "doi": data["doi"],
        "url": data["url"],
        "collections": split_pipe(data["collections"]),
        "tags": split_pipe(data["tags"]),
        "abstract": data["abstract_note"],
        "attachment_count": data["attachment_count"],
    }


def search_items(conn: sqlite3.Connection, query: str, limit: int) -> list[dict]:
    pattern = f"%{query.lower()}%"
    rows = conn.execute(SEARCH_SQL, {"pattern": pattern, "limit": limit}).fetchall()
    return [normalize_row(row) for row in rows]


def attachment_rows(conn: sqlite3.Connection, item_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT
            attachment_items.itemID,
            attachment_items.key,
            itemAttachments.contentType,
            itemAttachments.path
        FROM itemAttachments
        JOIN items AS attachment_items ON attachment_items.itemID = itemAttachments.itemID
        WHERE itemAttachments.parentItemID = ?
        ORDER BY attachment_items.itemID ASC
        """,
        (item_id,),
    ).fetchall()


def fetch_item(conn: sqlite3.Connection, zotero_dir: Path, item_id: int | None, key: str | None) -> dict | None:
    row = conn.execute(ITEM_SQL, {"item_id": item_id, "item_key": key}).fetchone()
    if row is None:
        return None
    item = normalize_row(row)
    attachments = []
    for attachment in attachment_rows(conn, item["item_id"]):
        attachments.append(
            {
                "item_id": attachment["itemID"],
                "key": attachment["key"],
                "content_type": attachment["contentType"],
                "raw_path": attachment["path"],
                "resolved_path": resolve_storage_path(zotero_dir, attachment["key"], attachment["path"]),
            }
        )
    item["attachments"] = attachments
    item["pdf_attachments"] = [
        entry for entry in attachments if entry["content_type"] == "application/pdf"
    ]
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared Zotero helper for the Research Vault")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("locate", help="Locate the Zotero data directory")

    search_parser = subparsers.add_parser("search", help="Search Zotero items")
    search_parser.add_argument("--query", required=True, help="Search term")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum results")

    item_parser = subparsers.add_parser("item", help="Fetch a single Zotero item")
    item_parser.add_argument("--item-id", type=int, help="Numeric Zotero item ID")
    item_parser.add_argument("--key", help="Zotero item key")

    args = parser.parse_args()

    zotero_dir = detect_zotero_dir()
    if zotero_dir is None:
        print(json.dumps({"error": "Zotero data directory not found"}))
        return 1

    if args.command == "locate":
        print(json.dumps({"zotero_dir": str(zotero_dir), "db_path": str(zotero_dir / "zotero.sqlite")}, ensure_ascii=False))
        return 0

    conn = connect(zotero_dir / "zotero.sqlite")
    try:
        if args.command == "search":
            payload = {
                "zotero_dir": str(zotero_dir),
                "query": args.query,
                "results": search_items(conn, args.query, args.limit),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

        if args.command == "item":
            if args.item_id is None and not args.key:
                print(json.dumps({"error": "Provide --item-id or --key"}))
                return 1
            item = fetch_item(conn, zotero_dir, args.item_id, args.key)
            if item is None:
                print(json.dumps({"error": "Item not found"}))
                return 1
            print(json.dumps(item, ensure_ascii=False, indent=2))
            return 0
    finally:
        conn.close()

    return 1


if __name__ == "__main__":
    sys.exit(main())
