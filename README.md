# bookstack

Git-managed content for the Sung family BookStack wiki at https://wiki.sung.us

## Structure
books/                  # All BookStack books (one .md file per book)
scripts/
export.py             # BookStack → books/ (always run first)
upload.py             # books/ → BookStack (managed books only)
config.example.py     # Copy to config location and fill in credentials
managed_books.json      # Auto-updated list of books with markdown content

## Setup

1. Copy `scripts/config.example.py` to your config location and fill in credentials:
   - Linux/Rivendell: `~/bookstack/config.py`
   - Windows: `C:\bookstack\config.py`

2. Install dependencies:
pip3 install requests

## Workflow

### AI workflow
1. Pull latest from GitHub: `git pull`
2. Export from BookStack: `python3 scripts/export.py`
3. Commit any human changes: `git add books/ managed_books.json && git commit -m "sync from BookStack"`
4. Make edits to files in `books/`
5. Commit edits: `git add books/ && git commit -m "describe changes"`
6. Dry run upload: `python3 scripts/upload.py --dry-run`
7. Upload: `python3 scripts/upload.py`
8. Push to GitHub: `git push`

### Human workflow
Edit directly in BookStack UI. Changes will be captured on next export.

## Book Tiers

- **Managed (Tier 1):** Books with markdown content — listed in `managed_books.json`
  — synced via Git workflow, uploaded by `upload.py`
- **Unmanaged (Tier 2):** WYSIWYG-only books — exported for reference but never uploaded
  — edit directly in BookStack UI only

`managed_books.json` is auto-updated by `export.py` on each full export run.
If a Tier 2 book is converted to markdown, it will automatically become Tier 1.

## Scripts

### export.py
Downloads all books from BookStack into `books/`.
Updates `managed_books.json` with books that have markdown content.
python3 scripts/export.py                    # export all books
python3 scripts/export.py --books network-TSs # export specific book
python3 scripts/export.py --dry-run          # preview only

### upload.py
Uploads managed books from `books/` to BookStack.
Only processes books in `managed_books.json`.
Skips WYSIWYG pages and unchanged content.
python3 scripts/upload.py                    # upload all managed books
python3 scripts/upload.py --books network-TSs # upload specific book
python3 scripts/upload.py --dry-run          # preview only
python3 scripts/upload.py --force            # skip diff check

## Notes

- Always run `export.py` before `upload.py` to capture any human edits
- Upload never deletes pages — only creates or updates
- Page matching is by H1 title in BookStack
- Chapter structure is preserved via `## Chapter:` markers in markdown
- Logs print to stdout — redirect to file if needed
