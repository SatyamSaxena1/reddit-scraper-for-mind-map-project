from pathlib import Path

from reddit_mindmap.inputs import extract_post_id, load_saved_links


def test_load_saved_links_csv(tmp_path: Path):
    path = tmp_path / "saved.csv"
    path.write_text("permalink\n/r/test/comments/abc/title/\n", encoding="utf-8")

    assert load_saved_links(path) == ["/r/test/comments/abc/title/"]


def test_load_saved_links_json(tmp_path: Path):
    path = tmp_path / "saved.json"
    path.write_text('[{"permalink": "/r/test/comments/abc/title/"}, "def456"]', encoding="utf-8")

    assert load_saved_links(path) == ["/r/test/comments/abc/title/", "def456"]


def test_extract_post_id():
    assert extract_post_id("/r/test/comments/abc123/title/") == "abc123"
    assert extract_post_id("abc123") == "abc123"
