"""Search index generation for client-side search."""

import json
import re

from .config import Config
from .post import Post
from .utils import write_file


def generate_search_index(posts: list[Post], config: Config) -> None:
    """Generate search_index.json for lunr.js client-side search."""
    index = []
    for post in posts:
        # Strip HTML tags for plain text body
        body = re.sub(r"<[^>]+>", "", post.content_html)
        body = re.sub(r"\s+", " ", body).strip()
        # Limit body length
        if len(body) > 5000:
            body = body[:5000]

        index.append({
            "url": post.url,
            "title": post.title,
            "date": post.date.strftime("%Y-%m-%d"),
            "tags": ", ".join(post.tags),
            "categories": ", ".join(post.categories),
            "excerpt": post.excerpt,
            "body": body,
        })

    output = config.public_dir / "search_index.json"
    write_file(output, json.dumps(index, ensure_ascii=False, indent=2))
