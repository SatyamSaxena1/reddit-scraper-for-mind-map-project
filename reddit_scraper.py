"""Backward-compatible entrypoint for the Reddit scraper.

Existing usage still works:
    python reddit_scraper.py --saved-file data/saved_posts.csv --output-dir output

New usage is available through:
    python -m reddit_mindmap scrape
    python -m reddit_mindmap export-vault
    python -m reddit_mindmap build-graph
"""

from reddit_mindmap.cli import main
from reddit_mindmap.config import DEFAULT_CONFIG, interactive_config
from reddit_mindmap.inputs import load_saved_links
from reddit_mindmap.scrape import fetch_all, inspect_for_403_reason

try:
    from reddit_mindmap.reddit_client import init_reddit, oauth_authorize
except ModuleNotFoundError:
    init_reddit = None
    oauth_authorize = None

try:
    from fastapi import FastAPI

    app = FastAPI()
except ModuleNotFoundError:
    app = None


if __name__ == "__main__":
    raise SystemExit(main())
