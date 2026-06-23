import csv
import json
from pathlib import Path
from typing import Iterable


def load_saved_links(file_path: str | Path) -> list[str]:
    """Load Reddit saved permalinks from CSV or JSON.

    CSV input must contain a ``permalink`` column. JSON input may be a list of
    permalink strings or objects containing ``permalink``.
    """
    path = Path(file_path)
    links: list[str] = []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                permalink = (row.get("permalink") or "").strip()
                if permalink:
                    links.append(permalink)
        return links

    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("JSON saved-links input must be a list")

    for item in data:
        if isinstance(item, str) and item.strip():
            links.append(item.strip())
        elif isinstance(item, dict) and item.get("permalink"):
            links.append(str(item["permalink"]).strip())
    return links


def extract_post_id(permalink: str) -> str:
    """Extract a Reddit submission ID from a permalink or raw ID."""
    value = permalink.strip().rstrip("/")
    if "/comments/" in value:
        return value.split("/comments/", 1)[1].split("/", 1)[0]
    return value.split("/")[-1]


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
