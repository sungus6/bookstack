# bookstack

Git-managed content for the Sung family BookStack wiki.

## Structure

- `books/` — Tier 1 AI-managed books (one markdown file per book)
- `scripts/` — export and upload scripts

## Workflow

### AI workflow
1. Pull latest from GitHub
2. Run `export.py` — syncs BookStack → `books/`
3. Edit markdown files
4. Commit and push changes
5. Run `upload.py` — syncs `books/` → BookStack

### Human workflow
Edit directly in BookStack UI. AI will capture changes on next export.

## Setup
Copy `scripts/config.example.py` to your local config location and fill in credentials.
- Windows: `C:\bookstack\config.py`
- Linux: `~/bookstack/config.py`
