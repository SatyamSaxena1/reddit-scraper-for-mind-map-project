from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScrapedPost:
    id: str
    permalink: str
    title: str
    selftext: str = ""
    author: str = "[deleted]"
    score: int | None = None
    subreddit: str = ""
    url: str = ""
    domain: str = ""
    created_utc: float | None = None
    comments: list[Any] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    fetched_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScrapedPost":
        return cls(
            id=str(data.get("id", "")),
            permalink=str(data.get("permalink", "")),
            title=str(data.get("title", "")),
            selftext=str(data.get("selftext", "") or ""),
            author=str(data.get("author", "[deleted]") or "[deleted]"),
            score=data.get("score"),
            subreddit=str(data.get("subreddit", "") or ""),
            url=str(data.get("url", "") or ""),
            domain=str(data.get("domain", "") or ""),
            created_utc=data.get("created_utc"),
            comments=data.get("comments") or [],
            media=data.get("media") or [],
            fetched_at=str(data.get("fetched_at", "") or ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "permalink": self.permalink,
            "title": self.title,
            "selftext": self.selftext,
            "author": self.author,
            "score": self.score,
            "subreddit": self.subreddit,
            "url": self.url,
            "domain": self.domain,
            "created_utc": self.created_utc,
            "comments": self.comments,
            "media": self.media,
            "fetched_at": self.fetched_at,
        }
