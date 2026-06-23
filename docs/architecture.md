# Architecture

This project is now organized as a local-first Reddit-to-Obsidian pipeline.

## Flow

1. Load saved Reddit permalinks from CSV or JSON.
2. Scrape posts with PRAW into normalized JSON files.
3. Export scraped JSON into a portable Obsidian vault folder.
4. Build `graph.json` from Markdown wiki links for a future browser graph viewer.

The original command still works:

```powershell
python .\reddit_scraper.py --saved-file data\saved_posts.csv --output-dir output
```

The new module CLI is:

```powershell
python -m reddit_mindmap scrape --saved-file data\saved_posts.csv --output-dir output
python -m reddit_mindmap export-vault --input-dir output --vault-dir vaults\reddit-mindmap
python -m reddit_mindmap build-graph --vault-dir vaults\reddit-mindmap --graph-out viewer\data\graph.json
```

## Local-first boundary

The first implementation does not require Azure, DigitalOcean, or an Obsidian plugin. The vault is just files on disk, which makes it portable and zero-cost when idle.
