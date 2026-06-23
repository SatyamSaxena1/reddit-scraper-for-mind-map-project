# reddit-scraper-for-mind-map-project

A local-first Reddit saved-post scraper that can export scraped content into a portable Obsidian vault and graph dataset for mind-mapping and analysis.

## Reddit Saved Posts Scraper

This repository provides a Python-friendly pipeline to scrape saved Reddit posts from a saved links CSV or JSON export, save normalized post/comment/media data, generate Obsidian-compatible Markdown notes, and build a graph JSON export for a future browser graph viewer.

Features
- Read saved links from CSV (`permalink` column) or JSON (list of strings or objects with `permalink`)
- Downloads images/videos when available
- Expands and collects comments
- Interactive CLI to provide Reddit credentials or use environment variables
- Error logging with simple error codes and `summary.json`
- Obsidian vault export with Markdown notes, YAML frontmatter, backlinks, entity notes, and indexes
- Graph JSON export generated from Markdown wiki links

Files
- `reddit_scraper.py` - backward-compatible main script
- `reddit_mindmap/` - package with scraper, vault export, and graph export modules
- `requirements.txt` - Python dependencies
- `.gitignore` - recommended ignores
- `.env.example` - safe environment variable template
- `docs/` - architecture, vault schema, and cloud cost-control notes
- `examples/` - small sample input/output fixtures

## Quickstart (Windows PowerShell)

1) Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3) Run the original scraper workflow:

```powershell
python .\reddit_scraper.py --saved-file data\saved_posts.csv --output-dir output --limit 10
```

4) Run non-interactive scraping with environment variables:

```powershell
$env:REDDIT_CLIENT_ID='your_id'
$env:REDDIT_CLIENT_SECRET='your_script_app_secret_or_blank_for_installed_app'
python .\reddit_scraper.py --non-interactive --saved-file data\saved_posts.csv --output-dir output
```

5) Use a Reddit installed/mobile app OAuth flow:

Create an app at `https://www.reddit.com/prefs/apps`, choose `installed app`, and set the redirect URI to:

```text
http://localhost:8080/authorize_callback
```

Then run:

```powershell
$env:REDDIT_CLIENT_ID='your_installed_app_client_id'
$env:REDDIT_CLIENT_SECRET=''
$env:REDDIT_USER_AGENT='reddit-mindmap/0.1 by your_reddit_username'
python -m reddit_mindmap scrape --oauth --saved-file data\saved_posts.csv --output-dir output --limit 25
```

The scraper prints a terminal progress bar as saved posts are extracted. Use `--no-progress` to disable it.

For Reddit's `web app` option, use the same redirect URI but set `REDDIT_CLIENT_SECRET` to the web app secret in your local terminal only. Do not paste or commit the secret.

6) Export scraped JSON into an Obsidian vault:

```powershell
python -m reddit_mindmap export-vault --input-dir output --vault-dir vaults\reddit-mindmap
```

7) Build graph JSON from the vault:

```powershell
python -m reddit_mindmap build-graph --vault-dir vaults\reddit-mindmap --graph-out viewer\data\graph.json
```

8) Open the browser graph viewer locally:

```powershell
python -m http.server 8000 --directory viewer
```

Then open `http://127.0.0.1:8000`.

9) Run the full local pipeline:

```powershell
python -m reddit_mindmap all --saved-file data\saved_posts.csv --output-dir output --vault-dir vaults\reddit-mindmap --limit 10
```

## Notes

- This repo intentionally does not include your CSV export of saved links; keep it locally under `data/` and pass `--saved-file data/saved_posts.csv`.
- Accessing private or NSFW posts may require a Reddit username/password for a script-type app or an OAuth flow.
- The first version is local-first. Azure and DigitalOcean should only be used later for optional scheduled processing, backups, or AI enrichment.
- Obsidian vault output is plain Markdown on disk, so it is portable and works without an Obsidian plugin.

## Security / secrets

- Do not put your `client_id`, `client_secret`, username, password, or cloud credentials into the repository.
- Use environment variables, a local ignored `.env`, Azure Key Vault, or DigitalOcean environment variables.
- Copy `.env.example` to a local `.env` only if you use one, and never commit real secrets.

## Testing

```powershell
python -m pytest
```

## DigitalOcean static viewer

The `.do/app.yaml` file describes a static App Platform deployment for `viewer/`.
Create the app only after this repo is pushed to GitHub:

```powershell
doctl apps create --spec .do\app.yaml
```

DigitalOcean auth should be done locally with `doctl auth init`. Do not paste tokens into chat or commit them.
