import json
import logging
from pathlib import Path
import time
from typing import Callable, Optional

import requests

from .inputs import extract_post_id, load_saved_links
from .media import download_media

logger = logging.getLogger(__name__)


def inspect_for_403_reason(permalink: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; RedditScraper/1.0)"}
        resp = requests.get(permalink, headers=headers, timeout=15)
        if resp.status_code == 403:
            text = resp.text.lower()
            if "private community" in text or "this community is private" in text:
                return "subreddit is private"
            if "over 18" in text or "nsfw" in text:
                return "age-gated / nsfw content"
            if "you are not allowed to view this community" in text:
                return "access restricted"
            return "403 response from reddit"
        if resp.status_code == 404:
            return "not found (404)"
        return f"HTTP {resp.status_code} response; check manually"
    except Exception as exc:
        return f"could not inspect permalink: {exc}"


def submission_to_dict(submission, post_id: str, permalink: str, media: list[dict]) -> dict:
    comments = []
    for comment in submission.comments.list():
        comments.append(
            {
                "id": getattr(comment, "id", ""),
                "author": comment.author.name if getattr(comment, "author", None) else "[deleted]",
                "body": getattr(comment, "body", ""),
                "score": getattr(comment, "score", None),
                "created_utc": getattr(comment, "created_utc", None),
                "permalink": f"https://www.reddit.com{getattr(comment, 'permalink', '')}" if getattr(comment, "permalink", "") else "",
            }
        )

    return {
        "id": post_id,
        "permalink": permalink,
        "title": submission.title,
        "selftext": submission.selftext,
        "author": submission.author.name if submission.author else "[deleted]",
        "score": submission.score,
        "subreddit": str(submission.subreddit) if getattr(submission, "subreddit", None) else "",
        "url": getattr(submission, "url", ""),
        "domain": getattr(submission, "domain", ""),
        "created_utc": getattr(submission, "created_utc", None),
        "comments": comments,
        "media": media,
        "fetched_at": time.asctime(),
    }


def collect_media(submission, post_id: str, output_dir: str | Path, inline_media: bool, inline_media_max_bytes: int) -> list[dict]:
    media: list[dict] = []
    preview = getattr(submission, "preview", None)
    if isinstance(preview, dict) and "images" in preview:
        for image in preview["images"]:
            url = image["source"]["url"].replace("&amp;", "&")
            try:
                media.append(download_media(post_id, url, output_dir, inline_media, inline_media_max_bytes))
            except Exception as exc:
                logger.warning("failed to download %s: %s", url, exc)
    elif getattr(submission, "url", "").lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".mp4")):
        try:
            media.append(download_media(post_id, submission.url, output_dir, inline_media, inline_media_max_bytes))
        except Exception as exc:
            logger.warning("failed to download %s: %s", submission.url, exc)
    return media


def fetch_all(
    reddit,
    saved_file: str = "saved_posts.csv",
    output_dir: str = "output",
    limit: Optional[int] = None,
    combined_file: Optional[str] = None,
    inline_media: bool = False,
    inline_media_max_bytes: int = 200000,
    sleep_seconds: float = 0.6,
    progress_callback: Optional[Callable[[int, int, dict], None]] = None,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    links = load_saved_links(saved_file)
    if limit is not None:
        links = links[:limit]

    results = []
    combined_fh = open(combined_file, "w", encoding="utf-8") if combined_file else None
    try:
        total = len(links)
        for index, link in enumerate(links, start=1):
            post_id = extract_post_id(link)
            entry = {"id": post_id, "permalink": link, "status_code": None, "error": None}
            try:
                submission = reddit.submission(id=post_id)
                submission.comments.replace_more(limit=None)
                media = collect_media(submission, post_id, output_path, inline_media, inline_media_max_bytes)
                data = submission_to_dict(submission, post_id, link, media)
                with (output_path / f"{post_id}.json").open("w", encoding="utf-8") as handle:
                    json.dump(data, handle, ensure_ascii=False, indent=2)
                if combined_fh:
                    combined_fh.write(json.dumps(data, ensure_ascii=False) + "\n")
                entry["status_code"] = 200
                logger.info("Saved %s -> %s", post_id, output_path / f"{post_id}.json")
                time.sleep(sleep_seconds)
            except Exception as exc:
                err_msg = str(exc)
                code = 500
                if "403" in err_msg or "forbidden" in err_msg.lower():
                    code = 403
                elif "404" in err_msg:
                    code = 404
                elif "timed out" in err_msg.lower() or "timeout" in err_msg.lower():
                    code = 408
                entry["status_code"] = code
                entry["error"] = err_msg
                logger.error("Error fetching %s: %s (code %s)", post_id, err_msg, code)
                with (output_path / "errors.log").open("a", encoding="utf-8") as log_handle:
                    log_handle.write(f"{time.asctime()} - {post_id} - {code} - {err_msg}\n")
            results.append(entry)
            if progress_callback:
                progress_callback(index, total, entry)
    finally:
        if combined_fh:
            combined_fh.close()

    with (output_path / "summary.json").open("w", encoding="utf-8") as summary:
        json.dump({"processed": len(links), "results": results}, summary, ensure_ascii=False, indent=2)
    return {"status": "Done processing posts", "processed": len(links), "results": results}
