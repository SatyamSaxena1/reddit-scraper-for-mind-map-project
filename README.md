# reddit-scraper-for-mind-map-project

It is what it says — a small tool for scraping your saved Reddit posts for later mind-mapping and analysis.

## Reddit Saved Posts Scraper

This repository provides a small tool to scrape saved Reddit posts (from a saved links CSV or a JSON export) and save each post's content, comments, and media to an output folder.

Features
- Read saved links from CSV (`permalink` column) or JSON (list of objects with `permalink`)
- Downloads images/videos when available
- Expands and collects comments
- Interactive CLI to provide Reddit credentials or use environment variables
- Error logging with simple error codes and `summary.json`

Files
- `reddit_scraper.py` - main script
- `requirements.txt` - Python dependencies
- `.gitignore` - recommended ignores

Quickstart (Windows PowerShell)

1) Create a virtual environment (optional but recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3) Run interactively:

```powershell
python .\reddit_scraper.py
```

4) Run non-interactive (use env vars or defaults):

```powershell
$env:REDDIT_CLIENT_ID='your_id'; $env:REDDIT_CLIENT_SECRET='your_secret'; python .\reddit_scraper.py --non-interactive
```

Notes
- This repo intentionally does not include your CSV export of saved links; add it to your machine under `data/` and pass `--saved-file data/saved_posts.csv`.
- Accessing private or NSFW posts may require a Reddit username/password (script-type app) or an OAuth flow.

Security / secrets
- Do NOT put your `client_id` or `client_secret` into the repository. Use environment variables (recommended) or a local secrets file excluded by `.gitignore`.

Publishing to GitHub
1. Create a new repository on GitHub (do not initialize with README/license).
2. In your local repo folder run:

```powershell
git init
git add .
git commit -m "Initial commit: reddit saved posts scraper"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

I'll add a recommended minimal CI workflow and contributing guide in the repo to make it easier for others to use.
