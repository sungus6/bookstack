#!/usr/bin/env python3
"""
export.py — Downloads all Tier 1 books from BookStack into books/

Usage:
    python3 export.py                          # export all books
    python3 export.py --books network-TSs      # export specific books
    python3 export.py --dry-run                # preview without writing files

Config: ~/bookstack/config.py (Linux) or C:\bookstack\config.py (Windows)
"""

import argparse
import importlib.util
import logging
import sys
import time
from datetime import datetime
from pathlib import Path


# -- Load config from outside repo
def load_config():
    candidates = [
        Path.home() / "bookstack" / "config.py",
        Path("C:/bookstack/config.py"),
    ]
    for path in candidates:
        if path.exists():
            spec = importlib.util.spec_from_file_location("config", path)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    print("ERROR: config.py not found. Copy scripts/config.example.py to ~/bookstack/config.py and fill in credentials.")
    sys.exit(1)


# -- Logging
def setup_logging():
    log = logging.getLogger("export")
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    log.addHandler(ch)
    return log


# -- API
def api_get(session, base_url, endpoint, log, max_retries=5):
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(f"{base_url}/api/{endpoint}", timeout=30)
            if r.status_code == 429:
                log.warning(f"Rate limited on {endpoint} — waiting {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"API error on {endpoint}: {e}")
            return None
    log.error(f"Giving up on {endpoint} after {max_retries} retries")
    return None


# -- Build markdown for a book
def build_book_markdown(book, pages_data, log):
    lines = []
    lines.append(f"# {book['name']}")
    lines.append(f"> Exported from BookStack on {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"> Slug: {book['slug']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Contents")
    lines.append("")
    current_chapter = None
    for page in pages_data:
        if page["chapter"] and page["chapter"] != current_chapter:
            lines.append(f"**{page['chapter']}**")
            current_chapter = page["chapter"]
        lines.append(f"- {page['name']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Page content
    current_chapter = None
    for page in pages_data:
        if page["chapter"] and page["chapter"] != current_chapter:
            lines.append(f"## Chapter: {page['chapter']}")
            lines.append("")
            current_chapter = page["chapter"]

        lines.append(f"### {page['name']}")
        lines.append("")

        content = page.get("markdown", "").strip()
        if not content:
            log.warning(f"  Page '{page['name']}' has no markdown content — may have been edited in WYSIWYG mode")
            content = "_No markdown content available. This page may have been edited in WYSIWYG mode._"

        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# -- Main
def main():
    parser = argparse.ArgumentParser(description="Export BookStack books to markdown")
    parser.add_argument("--books", nargs="+", metavar="SLUG", help="Export specific books by slug")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()

    log  = setup_logging()
    cfg  = load_config()

    try:
        import requests
    except ImportError:
        log.error("requests library not installed. Run: pip3 install requests")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Token {cfg.BOOKSTACK_TOKEN_ID}:{cfg.BOOKSTACK_TOKEN_SECRET}",
        "Content-Type":  "application/json",
    })

    books_dir = Path(cfg.BOOKS_DIR)

    log.info("=== BookStack Export started ===")
    if args.dry_run:
        log.warning("DRY RUN — no files will be written")

    # Fetch book list
    log.info("Fetching book list...")
    resp = api_get(session, cfg.BOOKSTACK_URL, "books?count=100", log)
    if not resp:
        log.error("Failed to fetch books. Check URL and credentials.")
        sys.exit(1)

    all_books = resp["data"]
    log.info(f"Found {len(all_books)} book(s) in BookStack")

    # Filter if --books specified
    if args.books:
        all_books = [b for b in all_books if b["slug"] in args.books]
        log.info(f"Filtering to: {', '.join(args.books)}")

    # Export each book
    for book in all_books:
        slug = book["slug"]
        name = book["name"]
        log.info(f"-- Book: '{name}' (slug: {slug})")

        time.sleep(0.3)
        detail = api_get(session, cfg.BOOKSTACK_URL, f"books/{book['id']}", log)
        if not detail:
            log.warning(f"  Skipping — could not fetch book detail")
            continue

        # Collect pages in order
        pages_data = []
        for item in detail.get("contents", []):
            if item["type"] == "page":
                time.sleep(0.3)
                page_detail = api_get(session, cfg.BOOKSTACK_URL, f"pages/{item['id']}", log)
                if page_detail:
                    pages_data.append({
                        "name":     page_detail["name"],
                        "chapter":  None,
                        "markdown": page_detail.get("markdown", ""),
                    })
            elif item["type"] == "chapter":
                for p in item.get("pages", []):
                    time.sleep(0.3)
                    page_detail = api_get(session, cfg.BOOKSTACK_URL, f"pages/{p['id']}", log)
                    if page_detail:
                        pages_data.append({
                            "name":     page_detail["name"],
                            "chapter":  item["name"],
                            "markdown": page_detail.get("markdown", ""),
                        })

        log.info(f"  Found {len(pages_data)} page(s)")

        if not pages_data:
            log.warning(f"  No pages — skipping")
            continue

        content = build_book_markdown(book, pages_data, log)
        out_file = books_dir / f"{slug}.md"

        if args.dry_run:
            log.info(f"  [DRY RUN] Would write: {out_file}")
        else:
            books_dir.mkdir(parents=True, exist_ok=True)
            out_file.write_text(content, encoding="utf-8")
            log.info(f"  Wrote: {out_file}")

    log.info("=== Export complete ===")


if __name__ == "__main__":
    main()
