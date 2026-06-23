import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from .inputs import unique_preserve_order
from .models import ScrapedPost

STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "from",
    "have",
    "into",
    "more",
    "that",
    "this",
    "with",
    "your",
    "what",
    "when",
    "where",
    "which",
    "will",
    "would",
}


def slugify(value: str, fallback: str = "untitled") -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:80].strip("-") or fallback


def note_name(prefix: str, value: str) -> str:
    clean = re.sub(r"\s+", " ", value).strip() or "unknown"
    return f"{prefix} - {clean}"


def safe_note_filename(title: str) -> str:
    return re.sub(r'[<>:"/\\|?*]+', "-", title).strip() or "untitled"


def yaml_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_list(values: list[str]) -> list[str]:
    return [f"  - {yaml_scalar(value)}" for value in values]


def frontmatter(data: dict) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(yaml_list(value))
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def markdown_escape(text: str) -> str:
    return (text or "").replace("\r\n", "\n").strip()


def comment_body(comment) -> str:
    if isinstance(comment, dict):
        author = comment.get("author") or "[deleted]"
        body = comment.get("body") or ""
        score = comment.get("score")
        suffix = f" (score {score})" if score is not None else ""
        return f"> **{author}**{suffix}: {body.replace(chr(10), chr(10) + '> ')}"
    return f"> {str(comment).replace(chr(10), chr(10) + '> ')}"


def infer_topics(post: ScrapedPost, max_topics: int = 6) -> list[str]:
    text = f"{post.title} {post.selftext}"
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", text)
    topics = []
    for word in words:
        clean = word.strip(".-").lower()
        if clean in STOPWORDS or len(clean) < 3:
            continue
        if clean not in topics:
            topics.append(clean)
        if len(topics) >= max_topics:
            break
    return topics


def load_posts(input_dir: str | Path) -> list[ScrapedPost]:
    posts = []
    for path in sorted(Path(input_dir).glob("*.json")):
        if path.name == "summary.json":
            continue
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        posts.append(ScrapedPost.from_dict(data))
    return posts


def copy_media(post: ScrapedPost, vault_dir: Path) -> list[str]:
    media_refs = []
    media_dir = vault_dir / "Media"
    media_dir.mkdir(parents=True, exist_ok=True)
    for item in post.media:
        if item.get("type") == "file" and item.get("path"):
            src = Path(item["path"])
            filename = item.get("filename") or src.name
            dest = media_dir / filename
            if src.exists():
                shutil.copy2(src, dest)
                media_refs.append(f"Media/{filename}")
            elif item.get("url"):
                media_refs.append(item["url"])
        elif item.get("url"):
            media_refs.append(item["url"])
        elif item.get("filename"):
            media_refs.append(item["filename"])
    return media_refs


def render_post_note(post: ScrapedPost, media_refs: list[str] | None = None) -> tuple[str, str, list[str]]:
    topics = infer_topics(post)
    topic_notes = [note_name("topic", topic) for topic in topics]
    subreddit_note = note_name("subreddit", post.subreddit) if post.subreddit else ""
    author_note = note_name("reddit user", post.author)
    title_slug = slugify(post.title, post.id)
    note_title = f"reddit post - {title_slug}"
    media_refs = media_refs or []
    source_url = post.permalink
    if source_url.startswith("/"):
        source_url = f"https://www.reddit.com{source_url}"
    domain = post.domain or (urlparse(post.url).netloc if post.url else "")

    metadata = {
        "type": "reddit_post",
        "reddit_id": post.id,
        "title": post.title,
        "subreddit": post.subreddit,
        "author": post.author,
        "score": post.score,
        "created_utc": post.created_utc,
        "permalink": source_url,
        "url": post.url,
        "domain": domain,
        "saved_source": "reddit_saved_export",
        "fetched_at": post.fetched_at,
        "tags": ["reddit", *(f"subreddit/{post.subreddit}" for _ in [0] if post.subreddit)],
        "topics": topics,
        "media": media_refs,
        "comment_count": len(post.comments),
    }
    lines = [
        frontmatter(metadata),
        "",
        f"# {post.title or post.id}",
        "",
        f"- Source: {source_url}",
        f"- External URL: {post.url}" if post.url else "",
        f"- Subreddit: [[{subreddit_note}]]" if subreddit_note else "",
        f"- Author: [[{author_note}]]",
        "",
        "## Topics",
        "",
        ", ".join(f"[[{topic}]]" for topic in topic_notes) if topic_notes else "_No inferred topics yet._",
        "",
        "## Post",
        "",
        markdown_escape(post.selftext) or "_No self text._",
    ]
    if media_refs:
        lines.extend(["", "## Media", ""])
        lines.extend(f"- {ref}" for ref in media_refs)
    if post.comments:
        lines.extend(["", "## Comments", ""])
        lines.extend(comment_body(comment) for comment in post.comments[:50])
        if len(post.comments) > 50:
            lines.append(f"\n_Comments truncated in note: {len(post.comments) - 50} additional comments remain in JSON._")
    links = unique_preserve_order([link for link in [subreddit_note, author_note, *topic_notes] if link])
    return note_title, "\n".join(line for line in lines if line != "") + "\n", links


def write_entity_note(path: Path, title: str, entity_type: str, description: str) -> None:
    if path.exists():
        return
    data = frontmatter({"type": entity_type, "title": title})
    path.write_text(f"{data}\n\n# {title}\n\n{description}\n", encoding="utf-8")


def export_vault(input_dir: str | Path, vault_dir: str | Path) -> dict:
    vault = Path(vault_dir)
    for folder in ["Posts", "Subreddits", "Authors", "Topics", "Media", "Indexes"]:
        (vault / folder).mkdir(parents=True, exist_ok=True)

    posts = load_posts(input_dir)
    exported = []
    all_subreddits: set[str] = set()
    all_authors: set[str] = set()
    all_topics: set[str] = set()

    for post in posts:
        media_refs = copy_media(post, vault)
        note_title, content, links = render_post_note(post, media_refs)
        filename = f"reddit-post-{post.id}-{slugify(post.title, post.id)}.md"
        (vault / "Posts" / filename).write_text(content, encoding="utf-8")
        exported.append({"id": post.id, "note": f"Posts/{filename}", "links": links})
        if post.subreddit:
            all_subreddits.add(post.subreddit)
        if post.author:
            all_authors.add(post.author)
        all_topics.update(infer_topics(post))

    for subreddit in sorted(all_subreddits):
        title = note_name("subreddit", subreddit)
        write_entity_note(vault / "Subreddits" / f"{safe_note_filename(title)}.md", title, "subreddit", "Reddit community entity note.")
    for author in sorted(all_authors):
        title = note_name("reddit user", author)
        write_entity_note(vault / "Authors" / f"{safe_note_filename(title)}.md", title, "reddit_author", "Reddit author entity note.")
    for topic in sorted(all_topics):
        title = note_name("topic", topic)
        write_entity_note(vault / "Topics" / f"{safe_note_filename(title)}.md", title, "topic", "Inferred topic entity note.")

    index = [
        frontmatter({"type": "index", "title": "Reddit Mind Map"}),
        "",
        "# Reddit Mind Map",
        "",
        f"Exported posts: {len(exported)}",
        "",
        "## Posts",
        "",
    ]
    index.extend(f"- [[{Path(item['note']).stem}]]" for item in exported)
    (vault / "Indexes" / "Reddit Mind Map.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    return {"posts": len(exported), "vault_dir": str(vault)}
