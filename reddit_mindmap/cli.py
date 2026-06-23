import argparse
import json
import os
import sys

from .config import DEFAULT_CONFIG, interactive_config
from .graph_export import export_graph
from .logging_utils import configure_logging
from .vault_export import export_vault


def add_scrape_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--saved-file", default="saved_posts.csv", help="Path to saved links CSV or JSON")
    parser.add_argument("--output-dir", default="output", help="Directory to store scraped JSON/media")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of posts to process")
    parser.add_argument("--non-interactive", action="store_true", help="Run without interactive prompts")
    parser.add_argument("--install-requirements", action="store_true", help="Install requirements before running")
    parser.add_argument("--combined-file", default=None, help="Write combined JSONL output")
    parser.add_argument("--inline-media", action="store_true", help="Inline small media in combined output")
    parser.add_argument("--inline-media-max-bytes", type=int, default=200000, help="Max media size to inline")
    parser.add_argument("--oauth", action="store_true", help="Run local browser OAuth flow before scraping")
    parser.add_argument("--no-progress", action="store_true", help="Disable terminal progress output")


def progress_bar(done: int, total: int, entry: dict) -> None:
    width = 28
    filled = int(width * done / total) if total else width
    bar = "#" * filled + "-" * (width - filled)
    status = "ok" if entry.get("status_code") == 200 else f"error {entry.get('status_code')}"
    print(f"\r[{bar}] {done}/{total} {status}: {entry.get('id')}", end="", flush=True)
    if done == total:
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reddit saved posts scraper and Obsidian vault exporter")
    subparsers = parser.add_subparsers(dest="command")

    scrape_parser = subparsers.add_parser("scrape", help="Scrape saved Reddit posts to JSON")
    add_scrape_args(scrape_parser)

    export_parser = subparsers.add_parser("export-vault", help="Convert scraped JSON into an Obsidian vault")
    export_parser.add_argument("--input-dir", default="output", help="Directory containing scraped post JSON files")
    export_parser.add_argument("--vault-dir", default="vaults/reddit-mindmap", help="Output Obsidian vault directory")

    graph_parser = subparsers.add_parser("build-graph", help="Generate graph JSON from an exported vault")
    graph_parser.add_argument("--vault-dir", default="vaults/reddit-mindmap", help="Obsidian vault directory")
    graph_parser.add_argument("--graph-out", default="viewer/data/graph.json", help="Graph JSON output path")

    all_parser = subparsers.add_parser("all", help="Scrape, export vault, and build graph JSON")
    add_scrape_args(all_parser)
    all_parser.add_argument("--vault-dir", default="vaults/reddit-mindmap", help="Output Obsidian vault directory")
    all_parser.add_argument("--graph-out", default="viewer/data/graph.json", help="Graph JSON output path")

    return parser


def run_scrape(args: argparse.Namespace) -> dict:
    from .reddit_client import init_reddit, oauth_authorize
    from .scrape import fetch_all

    if args.install_requirements:
        os.system(f"{sys.executable} -m pip install -r requirements.txt")

    cfg = DEFAULT_CONFIG if args.non_interactive else interactive_config()
    reddit = init_reddit(cfg)
    if args.oauth:
        oauth_authorize(reddit)
    return fetch_all(
        reddit,
        saved_file=args.saved_file,
        output_dir=args.output_dir,
        limit=args.limit,
        combined_file=args.combined_file,
        inline_media=args.inline_media,
        inline_media_max_bytes=args.inline_media_max_bytes,
        progress_callback=None if args.no_progress else progress_bar,
    )


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    raw_args = list(sys.argv[1:] if argv is None else argv)
    subcommands = {"scrape", "export-vault", "build-graph", "all"}

    # Backward compatibility: no subcommand means old scraper mode, including
    # legacy invocations such as ``python reddit_scraper.py --saved-file ...``.
    if raw_args and raw_args[0] in {"-h", "--help"}:
        parser = build_parser()
        args = parser.parse_args(raw_args)
    elif not raw_args or raw_args[0] not in subcommands:
        legacy_parser = argparse.ArgumentParser(description="Reddit saved posts scraper")
        add_scrape_args(legacy_parser)
        args = legacy_parser.parse_args(raw_args)
        args.command = "scrape"
    else:
        parser = build_parser()
        args = parser.parse_args(raw_args)

    if args.command == "scrape":
        result = run_scrape(args)
    elif args.command == "export-vault":
        result = export_vault(args.input_dir, args.vault_dir)
    elif args.command == "build-graph":
        result = export_graph(args.vault_dir, args.graph_out)
    elif args.command == "all":
        scrape_result = run_scrape(args)
        vault_result = export_vault(args.output_dir, args.vault_dir)
        graph_result = export_graph(args.vault_dir, args.graph_out)
        result = {"scrape": scrape_result, "vault": vault_result, "graph": graph_result}
    else:
        raise ValueError(f"unknown command: {args.command}")
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
