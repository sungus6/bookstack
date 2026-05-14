#!/usr/bin/env python3
"""
upload.py — Uploads managed books from books/ to BookStack.
            Only processes books listed in managed_books.json.
            Always run export.py first to sync any human changes.

Usage:
    python3 upload.py                          # upload all managed books
    python3 upload.py --books network-TSs      # upload specific books
    python3 upload.py --dry-run                # preview without changes
    python3 upload.py --force                  # skip content diff check

Config: ~/bookstack/config.py (Linux) or C:\bookstack\\config.py (Windows)
"""

import argparse
import importlib.util
import json
import logging
import re
import sys
import time
from pathlib import Path


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
    print("ERROR: config.py not found.")
    sys.exit(1)


def setup_logging():
    log = logging.getLogger("upload")
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
    ch  = logging.StreamHandler()
    ch.setFormatter(fmt)
    log.addHandler(ch)
    return log


def api_get(session, base_url, endpoint, log, max_retries=5):
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = session.get(f"{base_url}/api/{endpoint}", timeout=30)
            if r.status_code == 429:
                log.warning(f"Rate limited — waiting {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"GET {endpoint} failed: {e}")
            return None
    return None


def api_put(session, base_url, endpoint, body, log, max_retries=5):
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = session.put(f"{base_url}/api/{endpoint}", json=body, timeout=30)
            if r.status_code == 429:
                log.warning(f"Rate limited — waiting {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"PUT {endpoint} failed: {e}")
            return None
    return None


def api_post(session, base_url, endpoint, body, log, max_retries=5):
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            r = session.post(f"{base_url}/api/{endpoint}", json=body, timeout=30)
            if r.status_code == 429:
                log.warning(f"Rate limited — waiting {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"POST {endpoint} failed: {e}")
            return None
    return None


def parse_pages(content):
    """Parse ### headings into pages, preserving chapter assignments."""
    pages = []
    current_chapter = None
    current_title   = None
    current_lines   = []

    for line in content.splitlines():
        if re.match(r'^## Chapter:\s*(.+)$', line):
            current_chapter = re.match(r'^## Chapter:\s*(.+)$', line).group(1).strip()
        elif re.match(r'^### (.+)$', line):
            if current_title is not None:
                body = "\n".join(l for l in current_lines if not re.match(r'^---\s*$', l))
                pages.append({
                    "name":    current_title,
                    "chapter": current_chapter,
                    "content": body.strip(),
                })
            current_title = re.match(r'^### (.+)$', line).group(1).strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        body = "\n".join(l for l in current_lines if not re.match(r'^---\s*$', l))
        pages.append({
            "name":    current_title,
            "chapter": current_chapter,
            "content": body.strip(),
        })

    return pages


def get_book_title(content):
    for line in content.splitlines():
        m = re.match(r'^#\s+(.+)$', line)
        if m:
            return m.group(1).strip()
    return None


def main():
    parser = argparse.ArgumentParser(description="Upload managed books to BookStack")
    parser.add_argument("--books", nargs="+", metavar="SLUG", help="Upload specific books by slug")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--force",   action="store_true", help="Skip content diff, upload all pages")
    args = parser.parse_args()

    log = setup_logging()
    cfg = load_config()

    try:
        import requests
    except ImportError:
        log.error("requests not installed. Run: pip3 install requests --break-system-packages")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Token {cfg.BOOKSTACK_TOKEN_ID}:{cfg.BOOKSTACK_TOKEN_SECRET}",
        "Content-Type":  "application/json",
    })

    repo_root = Path(__file__).parent.parent
    books_dir = Path(cfg.BOOKS_DIR)

    log.info("=== BookStack Upload started ===")
    if args.dry_run:
        log.warning("DRY RUN — no changes will be made to BookStack")
    if args.force:
        log.warning("FORCE mode — skipping content diff, uploading all pages")

    # Load managed books list
    managed_path = repo_root / "managed_books.json"
    if not managed_path.exists():
        log.error("managed_books.json not found. Run export.py first.")
        sys.exit(1)

    managed_data  = json.loads(managed_path.read_text(encoding="utf-8"))
    managed_books = set(managed_data["managed_books"])
    log.info(f"Managed books: {len(managed_books)}")

    # Determine which books to process
    if args.books:
        slugs_to_process = args.books
        not_managed = [s for s in slugs_to_process if s not in managed_books]
        if not_managed:
            log.warning(f"These books are not in managed_books.json and will be skipped: {not_managed}")
        slugs_to_process = [s for s in slugs_to_process if s in managed_books]
    else:
        slugs_to_process = list(managed_books)

    if not slugs_to_process:
        log.warning("No books to process.")
        sys.exit(0)

    # Fetch all books from BookStack (slug -> id map)
    log.info("Fetching book list from BookStack...")
    resp = api_get(session, cfg.BOOKSTACK_URL, "books?count=100", log)
    if not resp:
        log.error("Failed to fetch books.")
        sys.exit(1)

    book_map = {b["slug"]: b["id"] for b in resp["data"]}

    # Stats
    stats = {"updated": 0, "created": 0, "skipped": 0, "errors": 0, "new_books": 0}

    for slug in slugs_to_process:
        md_file = books_dir / f"{slug}.md"
        if not md_file.exists():
            log.warning(f"-- {slug}: file not found in books/ — skipping")
            continue

        log.info(f"-- Book: {slug}")
        content = md_file.read_text(encoding="utf-8")

        # Create book if it doesn't exist in BookStack
        if slug not in book_map:
            title = get_book_title(content) or slug
            log.info(f"  Book not found in BookStack — creating: '{title}'")
            if args.dry_run:
                log.info(f"  [DRY RUN] Would create book: '{title}'")
                stats["new_books"] += 1
                continue
            new_book = api_post(session, cfg.BOOKSTACK_URL, "books", {"name": title}, log)
            if not new_book:
                log.error(f"  Failed to create book")
                stats["errors"] += 1
                continue
            book_map[new_book["slug"]] = new_book["id"]
            slug = new_book["slug"]
            stats["new_books"] += 1
            log.info(f"  Created book (id: {new_book['id']}, slug: {slug})")

        book_id = book_map[slug]

        # Fetch current book structure
        time.sleep(0.3)
        detail = api_get(session, cfg.BOOKSTACK_URL, f"books/{book_id}", log)
        if not detail:
            log.error(f"  Could not fetch book detail — skipping")
            stats["errors"] += 1
            continue

        # Build existing page map: name -> {id, chapter_id}
        existing_pages = {}
        chapter_map    = {}
        for item in detail.get("contents", []):
            if item["type"] == "page":
                existing_pages[item["name"]] = {"id": item["id"], "chapter_id": None}
            elif item["type"] == "chapter":
                chapter_map[item["name"]] = item["id"]
                for p in item.get("pages", []):
                    existing_pages[p["name"]] = {"id": p["id"], "chapter_id": item["id"]}

        # Parse pages from markdown file
        pages = parse_pages(content)
        log.info(f"  Found {len(pages)} page(s) in file")

        if not pages:
            log.warning(f"  No pages parsed — check file has '### Page Title' headings")
            continue

        file_had_errors = False

        for page in pages:
            name    = page["name"]
            content_md = page["content"]
            chapter = page["chapter"]

            # Skip WYSIWYG placeholder pages
            if content_md == "_No markdown content. This page was edited in WYSIWYG mode._":
                log.info(f"  SKIP '{name}' — WYSIWYG page, not managed")
                stats["skipped"] += 1
                continue

            time.sleep(0.3)

            if name in existing_pages:
                page_id = existing_pages[name]["id"]

                # Check if content changed
                if not args.force:
                    current = api_get(session, cfg.BOOKSTACK_URL, f"pages/{page_id}", log)
                    if current and current.get("markdown", "").strip() == content_md.strip():
                        log.info(f"  SKIP '{name}' — no changes")
                        stats["skipped"] += 1
                        continue

                if args.dry_run:
                    log.info(f"  [DRY RUN] Would UPDATE '{name}'")
                else:
                    result = api_put(session, cfg.BOOKSTACK_URL, f"pages/{page_id}",
                                     {"name": name, "markdown": content_md}, log)
                    if result:
                        log.info(f"  UPDATED '{name}'")
                        stats["updated"] += 1
                    else:
                        log.error(f"  FAILED to update '{name}'")
                        stats["errors"] += 1
                        file_had_errors = True
            else:
                if args.dry_run:
                    log.info(f"  [DRY RUN] Would CREATE '{name}'")
                else:
                    # Attach to chapter if specified
                    if chapter and chapter in chapter_map:
                        body = {"chapter_id": chapter_map[chapter], "name": name, "markdown": content_md}
                    else:
                        body = {"book_id": book_id, "name": name, "markdown": content_md}

                    result = api_post(session, cfg.BOOKSTACK_URL, "pages", body, log)
                    if result:
                        log.info(f"  CREATED '{name}'")
                        stats["created"] += 1
                    else:
                        log.error(f"  FAILED to create '{name}'")
                        stats["errors"] += 1
                        file_had_errors = True

    log.info("=== Upload complete ===")
    log.info(f"New books : {stats['new_books']}")
    log.info(f"Updated   : {stats['updated']}")
    log.info(f"Created   : {stats['created']}")
    log.info(f"Skipped   : {stats['skipped']}")
    log.info(f"Errors    : {stats['errors']}")


if __name__ == "__main__":
    main()
