import json
import re
from pathlib import Path
from typing import Any


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def node_type_from_path(path: Path) -> str:
    folder = path.parts[-2] if len(path.parts) >= 2 else ""
    return {
        "Posts": "post",
        "Subreddits": "subreddit",
        "Authors": "author",
        "Topics": "topic",
        "Media": "media",
        "Indexes": "index",
    }.get(folder, "note")


def edge_type(source_type: str, target: str) -> str:
    lowered = target.lower()
    if lowered.startswith("subreddit - "):
        return "posted_in"
    if lowered.startswith("reddit user - "):
        return "authored_by"
    if lowered.startswith("topic - "):
        return "tagged_topic"
    return "links_to"


def build_graph(vault_dir: str | Path) -> dict[str, Any]:
    vault = Path(vault_dir)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    for path in sorted(vault.rglob("*.md")):
        rel = path.relative_to(vault).as_posix()
        source_id = path.stem
        source_type = node_type_from_path(path)
        nodes[source_id] = {"id": source_id, "label": path.stem, "type": source_type, "path": rel}
        text = path.read_text(encoding="utf-8")
        for match in WIKILINK_RE.findall(text):
            target = match.strip()
            nodes.setdefault(target, {"id": target, "label": target, "type": "entity", "path": ""})
            edges.append(
                {
                    "id": f"{source_id}->{target}",
                    "source": source_id,
                    "target": target,
                    "type": edge_type(source_type, target),
                }
            )

    return {"nodes": list(nodes.values()), "edges": edges}


def export_graph(vault_dir: str | Path, graph_out: str | Path) -> dict[str, Any]:
    graph = build_graph(vault_dir)
    output = Path(graph_out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "graph_out": str(output)}
