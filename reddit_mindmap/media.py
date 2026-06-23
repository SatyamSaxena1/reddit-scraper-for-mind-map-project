import base64
import os
from pathlib import Path
from urllib.parse import urlparse

import requests


def media_filename(post_id: str, url: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path) or "media"
    return f"{post_id}_{name.split('?')[0]}"


def download_media(
    post_id: str,
    url: str,
    output_dir: str | Path,
    inline_media: bool = False,
    inline_media_max_bytes: int = 200000,
) -> dict:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    filename = media_filename(post_id, url)
    data = response.content
    if inline_media and len(data) <= inline_media_max_bytes:
        return {
            "type": "inline",
            "filename": filename,
            "data_base64": base64.b64encode(data).decode("ascii"),
            "mime": response.headers.get("Content-Type"),
            "url": url,
        }

    path = Path(output_dir) / filename
    path.write_bytes(data)
    return {"type": "file", "path": str(path), "url": url, "filename": filename}
