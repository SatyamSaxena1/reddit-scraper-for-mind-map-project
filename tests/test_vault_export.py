import json
from pathlib import Path

from reddit_mindmap.graph_export import build_graph, export_graph
from reddit_mindmap.vault_export import export_vault, render_post_note, slugify
from reddit_mindmap.models import ScrapedPost


def sample_post() -> dict:
    return {
        "id": "abc123",
        "permalink": "/r/MachineLearning/comments/abc123/title/",
        "title": "Useful LLM paper discussion",
        "selftext": "Retrieval and embeddings notes.",
        "author": "example_author",
        "score": 42,
        "subreddit": "MachineLearning",
        "url": "https://example.com/paper",
        "domain": "example.com",
        "created_utc": 1710000000,
        "comments": [{"author": "commenter", "body": "Great reference.", "score": 5}],
        "media": [],
        "fetched_at": "Mon Jan 01 00:00:00 2026",
    }


def test_slugify():
    assert slugify("Hello, Obsidian Graph!") == "hello-obsidian-graph"


def test_render_post_note_has_frontmatter_and_links():
    _, content, links = render_post_note(ScrapedPost.from_dict(sample_post()))

    assert "type: \"reddit_post\"" in content
    assert "[[subreddit - MachineLearning]]" in content
    assert "[[reddit user - example_author]]" in content
    assert "subreddit - MachineLearning" in links


def test_export_vault_and_graph(tmp_path: Path):
    input_dir = tmp_path / "output"
    vault_dir = tmp_path / "vault"
    graph_out = tmp_path / "viewer" / "data" / "graph.json"
    input_dir.mkdir()
    (input_dir / "abc123.json").write_text(json.dumps(sample_post()), encoding="utf-8")

    result = export_vault(input_dir, vault_dir)
    graph_result = export_graph(vault_dir, graph_out)
    graph = build_graph(vault_dir)

    assert result["posts"] == 1
    assert (vault_dir / "Posts" / "reddit-post-abc123-useful-llm-paper-discussion.md").exists()
    assert (vault_dir / "Subreddits" / "subreddit - MachineLearning.md").exists()
    assert graph_result["nodes"] >= 3
    assert any(edge["type"] == "posted_in" for edge in graph["edges"])
