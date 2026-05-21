#!/usr/bin/env python3
"""
Upload clan markdown files to BookStack.
Uses BookStack chapters to group pages by person.
Format: ## = chapter, ### = page (1 page per person with all consolidated info)
"""
import sys, os, re, requests, json

sys.path.insert(0, "/home/aule/bookstack")
from config import BOOKSTACK_URL, BOOKSTACK_TOKEN_ID, BOOKSTACK_TOKEN_SECRET, BOOKS_DIR

s = requests.Session()
s.headers.update({"Authorization": f"Token {BOOKSTACK_TOKEN_ID}:{BOOKSTACK_TOKEN_SECRET}"})
s.headers.update({"Content-Type": "application/json"})

CLANS_SHELF_ID = 366

def parse_markdown(filepath):
    """Parse markdown into pages with chapter groupings."""
    with open(filepath, "r") as f:
        content = f.read()

    lines = content.split("\n")
    book_title = None
    book_slug = None
    pages = []  # list of {name, content, chapter}
    current_chapter = None
    current_page_name = None
    current_page_lines = []

    for line in lines:
        m = re.match(r"^# (.+)$", line)
        if m:
            book_title = m.group(1).strip()
            continue

        m = re.match(r"^> Slug: (.+)$", line)
        if m:
            book_slug = m.group(1).strip()
            continue

        m = re.match(r"^## [Cc]hapter: (.+)$", line)
        if m:
            # Save previous page
            if current_page_name:
                pages.append({
                    "name": current_page_name,
                    "chapter": current_chapter,
                    "content": "\n".join(current_page_lines)
                })
            current_chapter = m.group(1).strip()
            current_page_name = None
            current_page_lines = []
            continue

        m = re.match(r"^### (.+)$", line)
        if m:
            if current_page_name:
                pages.append({
                    "name": current_page_name,
                    "chapter": current_chapter,
                    "content": "\n".join(current_page_lines)
                })
            current_page_name = m.group(1).strip()
            current_page_lines = []
            continue

        if current_page_name is not None:
            current_page_lines.append(line)

    if current_page_name:
        pages.append({
            "name": current_page_name,
            "chapter": current_chapter,
            "content": "\n".join(current_page_lines)
        })

    return book_title, book_slug, pages


def create_book(title, slug):
    """Create a new book."""
    payload = {
        "name": title,
        "slug": slug,
        "description": f"Part of the Clans shelf — {title} family history, profiles, and records."
    }
    r = s.post(f"{BOOKSTACK_URL}/api/books", json=payload, timeout=30)
    if r.status_code == 200:
        b = r.json()
        print(f"  Created book: [{b['id']}] {b['name']} (slug: {b['slug']})")
        return b["id"]
    else:
        print(f"  ✗ Error creating book: {r.status_code} {r.text[:300]}")
        return None


def find_or_create_chapter(book_id, chapter_name):
    """Find existing chapter by name, or create a new one."""
    # List chapters
    r = s.get(f"{BOOKSTACK_URL}/api/books/{book_id}", timeout=30)
    if r.status_code == 200:
        # Try to find chapters by getting pages with chapter_id
        pass

    # Create chapter
    payload = {
        "book_id": book_id,
        "name": chapter_name
    }
    r = s.post(f"{BOOKSTACK_URL}/api/chapters", json=payload, timeout=30)
    if r.status_code == 200:
        ch = r.json()
        print(f"    Chapter created: [{ch['id']}] {ch['name']}")
        return ch["id"]
    elif r.status_code == 422 and "already" in r.text.lower():
        # Chapter already exists — find it
        r2 = s.get(f"{BOOKSTACK_URL}/api/books/{book_id}?include=chapters", timeout=30)
        if r2.status_code == 200:
            for ch in r2.json().get("chapters", []):
                if ch["name"].strip().lower() == chapter_name.strip().lower():
                    print(f"    Found existing chapter: [{ch['id']}] {ch['name']}")
                    return ch["id"]
        print(f"    ✗ Chapter error: {r.status_code} {r.text[:200]}")
        return None
    else:
        print(f"    ✗ Chapter error: {r.status_code} {r.text[:200]}")
        return None


def create_page(book_id, name, content, chapter_id=None):
    """Create a page in the book, optionally under a chapter."""
    payload = {
        "book_id": book_id,
        "name": name,
        "markdown": content
    }
    if chapter_id:
        payload["chapter_id"] = chapter_id

    r = s.post(f"{BOOKSTACK_URL}/api/pages", json=payload, timeout=30)
    if r.status_code == 200:
        p = r.json()
        print(f"    ✓ {p['name']}")
        return p["id"]
    else:
        print(f"    ✗ Error creating '{name}': {r.status_code} {r.text[:200]}")
        return None


def add_book_to_shelf(book_id, shelf_id):
    """Add a book to the Clans shelf."""
    r = s.get(f"{BOOKSTACK_URL}/api/shelves/{shelf_id}", timeout=30)
    if r.status_code == 200:
        current_books = [b["id"] for b in r.json().get("books", [])]
        if book_id not in current_books:
            current_books.append(book_id)
            r = s.put(f"{BOOKSTACK_URL}/api/shelves/{shelf_id}", json={"books": current_books}, timeout=30)
            if r.status_code == 200:
                print(f"    Added to shelf")
            else:
                print(f"    ✗ Error adding to shelf: {r.status_code}")
    else:
        print(f"    ✗ Could not get shelf: {r.status_code}")


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else ["sung-clan.md", "song-clan.md", "shinn-clan.md", "lee-clan.md"]

    for fname in files:
        filepath = os.path.join(BOOKS_DIR, fname)
        if not os.path.exists(filepath):
            print(f"\n✗ File not found: {filepath}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {fname}")
        print(f"{'='*60}")

        title, slug, pages = parse_markdown(filepath)
        if not title or not slug:
            print(f"  ✗ Could not parse title/slug from {fname}")
            continue

        print(f"  Title: {title}")
        print(f"  Pages: {len(pages)}")

        # Create book
        bid = create_book(title, slug)
        if not bid:
            continue

        # Add to shelf
        add_book_to_shelf(bid, CLANS_SHELF_ID)

        # Create chapters and pages
        chapter_cache = {}  # chapter_name -> chapter_id
        for page in pages:
            chapter_id = None
            if page.get("chapter"):
                if page["chapter"] not in chapter_cache:
                    cid = find_or_create_chapter(bid, page["chapter"])
                    if cid:
                        chapter_cache[page["chapter"]] = cid
                chapter_id = chapter_cache.get(page["chapter"])

            create_page(bid, page["name"], page["content"], chapter_id)

        print(f"  ✓ Done — {len(pages)} pages in {len(chapter_cache)} chapters")

    print(f"\n✓ All books uploaded.")


if __name__ == "__main__":
    main()
