#!/usr/bin/env python3
"""
Paper Add — Find, download, and add papers to Zotero.

Usage:
  python3 paper_add.py --doi "10.1007/s00707-013-1057-1"
  python3 paper_add.py --title "micromechanics multiscale model nonlinear composites" --author "Zhang"
  python3 paper_add.py --doi "10.1007/s00707-013-1057-1" --no-download  # metadata only

Requires: requests, playwright (with chromium)
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import string
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


# --- Zotero path detection ---

def find_zotero_dir():
    """Auto-detect Zotero data directory based on OS."""
    import platform
    system = platform.system()

    if system == "Linux":
        # Check WSL
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    # WSL — find Windows username
                    result = subprocess.run(
                        ["cmd.exe", "/C", "echo %USERNAME%"],
                        capture_output=True, text=True, timeout=5
                    )
                    win_user = result.stdout.strip()
                    zotero_dir = f"/mnt/c/Users/{win_user}/Zotero"
                    if os.path.exists(zotero_dir):
                        return zotero_dir
        except Exception:
            pass
        # Native Linux
        home_zotero = os.path.expanduser("~/Zotero")
        if os.path.exists(home_zotero):
            return home_zotero

    elif system == "Darwin":
        home_zotero = os.path.expanduser("~/Zotero")
        if os.path.exists(home_zotero):
            return home_zotero

    # Fallback: search for zotero.sqlite
    home = os.path.expanduser("~")
    for root, dirs, files in os.walk(home):
        if "zotero.sqlite" in files:
            return root
        # Don't go too deep
        if root.count(os.sep) - home.count(os.sep) > 3:
            dirs.clear()

    return None


# --- Metadata fetching ---

def fetch_metadata_by_doi(doi):
    """Fetch paper metadata from CrossRef API."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    headers = {"User-Agent": "PaperAdd/1.0 (mailto:research@example.com)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            item = data["message"]
            authors = []
            for a in item.get("author", []):
                authors.append({
                    "firstName": a.get("given", ""),
                    "lastName": a.get("family", "")
                })
            return {
                "title": item.get("title", [""])[0],
                "authors": authors,
                "date": str(item.get("issued", {}).get("date-parts", [[""]])[0][0]),
                "journal": item.get("container-title", [""])[0],
                "volume": item.get("volume", ""),
                "issue": item.get("issue", ""),
                "pages": item.get("page", ""),
                "doi": doi,
                "url": item.get("URL", f"https://doi.org/{doi}"),
                "issn": item.get("ISSN", [""])[0] if item.get("ISSN") else "",
            }
    except Exception as e:
        print(f"[WARN] CrossRef lookup failed: {e}")
        return None


def search_semantic_scholar(title, author=None):
    """Search Semantic Scholar for a paper by title, return DOI if found."""
    query = title
    if author:
        query = f"{author} {title}"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit=5&fields=title,externalIds,authors,year,venue"
    headers = {"User-Agent": "PaperAdd/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("data", [])
            if results:
                for r in results:
                    ext = r.get("externalIds", {})
                    if ext.get("DOI"):
                        return {
                            "doi": ext["DOI"],
                            "title": r.get("title", ""),
                            "year": r.get("year"),
                            "venue": r.get("venue", ""),
                            "authors": [{"firstName": "", "lastName": a["name"]} for a in r.get("authors", [])]
                        }
    except Exception as e:
        print(f"[WARN] Semantic Scholar search failed: {e}")
    return None


# --- PDF finding and downloading ---

def find_open_access_pdf(doi, email="research@example.com"):
    """Use Unpaywall API to find open access PDF."""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi, safe='')}?email={email}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PaperAdd/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            best = data.get("best_oa_location")
            if best and best.get("url_for_pdf"):
                return best["url_for_pdf"]
            # Try other locations
            for loc in data.get("oa_locations", []):
                if loc.get("url_for_pdf"):
                    return loc["url_for_pdf"]
    except Exception as e:
        print(f"[INFO] Unpaywall: no open access found ({e})")
    return None


def crawl_for_pdf(doi, title):
    """Use Playwright (headless Chrome) to crawl for PDF links."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[WARN] Playwright not installed, skipping browser crawl")
        return None

    pdf_url = None
    search_query = f'{title} filetype:pdf'

    print(f"[INFO] Crawling Google Scholar for PDF...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

            # Try Google Scholar
            scholar_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(title)}"
            page.goto(scholar_url, timeout=20000)
            time.sleep(2)

            # Look for PDF links
            links = page.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text() or ""
                if href.endswith(".pdf") or "[PDF]" in text:
                    pdf_url = href
                    print(f"[INFO] Found PDF link: {pdf_url}")
                    break

            # Try ResearchGate if no PDF found
            if not pdf_url:
                print("[INFO] Trying ResearchGate...")
                rg_url = f"https://www.researchgate.net/search?q={urllib.parse.quote(title)}"
                page.goto(rg_url, timeout=20000)
                time.sleep(2)

                links = page.query_selector_all("a")
                for link in links:
                    href = link.get_attribute("href") or ""
                    if "/publication/" in href and "figure" not in href:
                        # Found a publication page, check for PDF
                        full_url = href if href.startswith("http") else f"https://www.researchgate.net{href}"
                        page.goto(full_url, timeout=20000)
                        time.sleep(2)
                        pdf_links = page.query_selector_all("a[href*='.pdf']")
                        if pdf_links:
                            pdf_url = pdf_links[0].get_attribute("href")
                            print(f"[INFO] Found PDF on ResearchGate: {pdf_url}")
                        break

            # Try DOI direct (some publishers serve PDF)
            if not pdf_url and doi:
                print("[INFO] Trying publisher direct...")
                doi_url = f"https://doi.org/{doi}"
                page.goto(doi_url, timeout=20000)
                time.sleep(3)
                # Check if we landed on a page with PDF link
                pdf_links = page.query_selector_all("a[href*='.pdf'], a:has-text('Download PDF'), a:has-text('Full Text PDF')")
                for link in pdf_links:
                    href = link.get_attribute("href") or ""
                    if href:
                        pdf_url = href if href.startswith("http") else urllib.parse.urljoin(page.url, href)
                        print(f"[INFO] Found PDF on publisher site: {pdf_url}")
                        break

            browser.close()

    except Exception as e:
        print(f"[WARN] Browser crawl failed: {e}")

    return pdf_url


def download_pdf(url, output_path):
    """Download PDF from URL."""
    print(f"[INFO] Downloading PDF from: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            # Verify it's actually a PDF
            if content[:4] == b'%PDF':
                with open(output_path, 'wb') as f:
                    f.write(content)
                print(f"[OK] PDF saved: {output_path} ({len(content)} bytes)")
                return True
            else:
                print(f"[WARN] Downloaded file is not a PDF (starts with: {content[:20]})")
                return False
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return False


# --- Zotero integration ---

def generate_zotero_key():
    """Generate an 8-character Zotero-style key."""
    import random
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


def add_to_zotero(zotero_dir, metadata, pdf_path=None):
    """Add paper to Zotero SQLite database and storage."""
    db_path = os.path.join(zotero_dir, "zotero.sqlite")
    if not os.path.exists(db_path):
        print(f"[ERROR] Zotero database not found: {db_path}")
        return False

    item_key = generate_zotero_key()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Get the itemTypeID for "journalArticle"
        cur.execute("SELECT itemTypeID FROM itemTypes WHERE typeName = 'journalArticle'")
        article_type_id = cur.fetchone()[0]

        # Get libraryID (usually 1 for personal library)
        cur.execute("SELECT libraryID FROM libraries LIMIT 1")
        library_id = cur.fetchone()[0]

        # Insert item
        cur.execute("""
            INSERT INTO items (itemTypeID, libraryID, key, dateAdded, dateModified, clientDateModified, version)
            VALUES (?, ?, ?, datetime('now'), datetime('now'), datetime('now'), 0)
        """, (article_type_id, library_id, item_key))
        item_id = cur.lastrowid

        # Insert metadata fields
        field_map = {
            "title": metadata.get("title", ""),
            "date": metadata.get("date", ""),
            "publicationTitle": metadata.get("journal", ""),
            "volume": metadata.get("volume", ""),
            "issue": metadata.get("issue", ""),
            "pages": metadata.get("pages", ""),
            "DOI": metadata.get("doi", ""),
            "url": metadata.get("url", ""),
            "ISSN": metadata.get("issn", ""),
            "abstractNote": metadata.get("abstract", ""),
        }

        for field_name, value in field_map.items():
            if not value:
                continue
            # Get fieldID
            cur.execute("SELECT fieldID FROM fields WHERE fieldName = ?", (field_name,))
            row = cur.fetchone()
            if not row:
                continue
            field_id = row[0]

            # Get or create valueID
            cur.execute("SELECT valueID FROM itemDataValues WHERE value = ?", (value,))
            row = cur.fetchone()
            if row:
                value_id = row[0]
            else:
                cur.execute("INSERT INTO itemDataValues (value) VALUES (?)", (value,))
                value_id = cur.lastrowid

            cur.execute("INSERT INTO itemData (itemID, fieldID, valueID) VALUES (?, ?, ?)",
                        (item_id, field_id, value_id))

        # Insert authors
        cur.execute("SELECT creatorTypeID FROM creatorTypes WHERE creatorType = 'author'")
        author_type_id = cur.fetchone()[0]

        for i, author in enumerate(metadata.get("authors", [])):
            first = author.get("firstName", "")
            last = author.get("lastName", "")
            if not last:
                continue

            # Check if creator exists
            cur.execute("SELECT creatorID FROM creators WHERE firstName = ? AND lastName = ?",
                        (first, last))
            row = cur.fetchone()
            if row:
                creator_id = row[0]
            else:
                cur.execute("INSERT INTO creators (firstName, lastName, fieldMode) VALUES (?, ?, 0)",
                            (first, last))
                creator_id = cur.lastrowid

            cur.execute("""
                INSERT INTO itemCreators (itemID, creatorID, creatorTypeID, orderIndex)
                VALUES (?, ?, ?, ?)
            """, (item_id, creator_id, author_type_id, i))

        # Handle PDF attachment
        if pdf_path and os.path.exists(pdf_path):
            attach_key = generate_zotero_key()
            storage_dir = os.path.join(zotero_dir, "storage", attach_key)
            os.makedirs(storage_dir, exist_ok=True)

            # Create filename: "Author1 and Author2 - Year - Title.pdf"
            authors = metadata.get("authors", [])
            if len(authors) == 1:
                author_str = authors[0]["lastName"]
            elif len(authors) == 2:
                author_str = f"{authors[0]['lastName']} and {authors[1]['lastName']}"
            elif len(authors) > 2:
                author_str = f"{authors[0]['lastName']} et al."
            else:
                author_str = "Unknown"

            year = metadata.get("date", "")
            title_short = metadata.get("title", "Unknown")[:80]
            pdf_filename = f"{author_str} - {year} - {title_short}.pdf"
            # Clean filename
            pdf_filename = re.sub(r'[<>:"/\\|?*]', '', pdf_filename)

            dest_path = os.path.join(storage_dir, pdf_filename)
            shutil.copy2(pdf_path, dest_path)

            # Get attachment itemTypeID
            cur.execute("SELECT itemTypeID FROM itemTypes WHERE typeName = 'attachment'")
            attach_type_id = cur.fetchone()[0]

            # Insert attachment item
            cur.execute("""
                INSERT INTO items (itemTypeID, libraryID, key, dateAdded, dateModified, clientDateModified, version)
                VALUES (?, ?, ?, datetime('now'), datetime('now'), datetime('now'), 0)
            """, (attach_type_id, library_id, attach_key))
            attach_item_id = cur.lastrowid

            # Insert attachment record
            cur.execute("""
                INSERT INTO itemAttachments (itemID, parentItemID, linkMode, contentType, path)
                VALUES (?, ?, 1, 'application/pdf', ?)
            """, (attach_item_id, item_id, f"storage:{pdf_filename}"))

            print(f"[OK] PDF attached: {dest_path}")

        conn.commit()
        print(f"[OK] Added to Zotero: key={item_key}, itemID={item_id}")
        print(f"     Title: {metadata.get('title', 'N/A')}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Zotero insertion failed: {e}")
        return False
    finally:
        conn.close()


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Find, download, and add papers to Zotero")
    parser.add_argument("--doi", help="Paper DOI")
    parser.add_argument("--title", help="Paper title (for search)")
    parser.add_argument("--author", help="Author name (for search)")
    parser.add_argument("--no-download", action="store_true", help="Metadata only, no PDF download")
    parser.add_argument("--zotero-dir", help="Zotero data directory (auto-detected if omitted)")
    parser.add_argument("--collection", help="Zotero collection name to add to")
    args = parser.parse_args()

    if not args.doi and not args.title:
        print("Error: provide --doi or --title")
        sys.exit(1)

    # Step 1: Find Zotero
    zotero_dir = args.zotero_dir or find_zotero_dir()
    if not zotero_dir:
        print("[ERROR] Cannot find Zotero data directory")
        sys.exit(1)
    print(f"[INFO] Zotero dir: {zotero_dir}")

    # Step 2: Get DOI if not provided
    doi = args.doi
    metadata = None

    if not doi and args.title:
        print(f"[INFO] Searching Semantic Scholar for: {args.title}")
        result = search_semantic_scholar(args.title, args.author)
        if result:
            doi = result["doi"]
            print(f"[OK] Found DOI: {doi}")
        else:
            print("[ERROR] Could not find DOI. Try providing --doi directly.")
            sys.exit(1)

    # Step 3: Fetch metadata
    print(f"[INFO] Fetching metadata for DOI: {doi}")
    metadata = fetch_metadata_by_doi(doi)
    if not metadata:
        print("[ERROR] Could not fetch metadata from CrossRef")
        sys.exit(1)

    print(f"[OK] Title: {metadata['title']}")
    print(f"     Authors: {', '.join(a['lastName'] for a in metadata['authors'])}")
    print(f"     Journal: {metadata['journal']} ({metadata['date']})")

    # Step 4: Find and download PDF
    pdf_path = None
    if not args.no_download:
        # Try Unpaywall first (fast, legal)
        print("[INFO] Searching for open access PDF (Unpaywall)...")
        pdf_url = find_open_access_pdf(doi)

        # Try browser crawl if Unpaywall fails
        if not pdf_url:
            print("[INFO] No open access found. Trying browser crawl...")
            pdf_url = crawl_for_pdf(doi, metadata["title"])

        if pdf_url:
            tmp_path = f"/tmp/paper_{doi.replace('/', '_')}.pdf"
            if download_pdf(pdf_url, tmp_path):
                pdf_path = tmp_path
        else:
            print("[WARN] Could not find downloadable PDF")
            print("       Try: GIST library proxy or manual download")

    # Step 5: Add to Zotero
    print("[INFO] Adding to Zotero...")
    success = add_to_zotero(zotero_dir, metadata, pdf_path)

    # Cleanup temp PDF
    if pdf_path and os.path.exists(pdf_path):
        os.remove(pdf_path)

    # Summary
    print("\n" + "=" * 50)
    if success:
        print("RESULT: Successfully added to Zotero")
        print(f"  Title: {metadata['title']}")
        print(f"  DOI: {doi}")
        print(f"  PDF: {'attached' if pdf_path else 'not found — add manually'}")
        if not pdf_path:
            print(f"\n  Manual PDF sources:")
            print(f"    - GIST Library: https://doi.org/{doi}")
            print(f"    - Google Scholar: https://scholar.google.com/scholar?q={urllib.parse.quote(metadata['title'])}")
    else:
        print("RESULT: Failed to add to Zotero")
    print("=" * 50)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
