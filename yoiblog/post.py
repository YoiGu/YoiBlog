"""Post and Page models for YoiBlog."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import frontmatter
import markdown

from .utils import slugify, truncate_html


@dataclass
class Post:
    title: str
    slug: str
    date: datetime
    updated: Optional[datetime] = None
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    excerpt: str = ""
    content_md: str = ""
    content_html: str = ""
    source_path: Optional[Path] = None
    url: str = ""
    draft: bool = False
    toc: str = ""
    cover: str = ""

    @classmethod
    def from_file(cls, filepath: Path, md_config: dict) -> "Post":
        """Parse a markdown file into a Post object."""
        fm = frontmatter.load(str(filepath))

        title = fm.get("title", filepath.stem)
        slug = fm.get("slug", slugify(title))
        date = _parse_date(fm.get("date"), filepath)
        if fm.get("updated"):
            updated = _parse_date(fm.get("updated"))
        else:
            # Fallback to file modification time
            updated = datetime.fromtimestamp(filepath.stat().st_mtime)
        tags = _ensure_list(fm.get("tags", []))
        categories = _ensure_list(fm.get("categories", []))
        draft = fm.get("draft", False)
        cover = fm.get("cover", "")

        # Render markdown
        md = _create_markdown(md_config)
        content_html = md.convert(fm.content)
        toc = getattr(md, "toc", "")

        # Extract excerpt
        excerpt = fm.get("excerpt", "")
        if not excerpt:
            excerpt = truncate_html(content_html, 200)

        return cls(
            title=title,
            slug=slug,
            date=date,
            updated=updated,
            tags=tags,
            categories=categories,
            excerpt=excerpt,
            content_md=fm.content,
            content_html=content_html,
            source_path=filepath,
            draft=draft,
            toc=toc,
            cover=cover,
        )

    def build_url(self, permalink_pattern: str) -> str:
        """Build the URL for this post based on permalink pattern."""
        url = permalink_pattern
        url = url.replace(":year", self.date.strftime("%Y"))
        url = url.replace(":month", self.date.strftime("%m"))
        url = url.replace(":day", self.date.strftime("%d"))
        url = url.replace(":slug", self.slug)
        url = url.replace(":title", self.slug)
        if not url.startswith("/"):
            url = "/" + url
        if not url.endswith("/"):
            url += "/"
        self.url = url
        return url


@dataclass
class Page:
    title: str
    slug: str
    content_md: str = ""
    content_html: str = ""
    source_path: Optional[Path] = None
    url: str = ""
    toc: str = ""
    layout: str = "page"

    @classmethod
    def from_file(cls, filepath: Path, md_config: dict) -> "Page":
        """Parse a markdown file into a Page object."""
        fm = frontmatter.load(str(filepath))

        title = fm.get("title", filepath.stem.replace("-", " ").title())
        slug = fm.get("slug", slugify(title))
        layout = fm.get("layout", "page")

        md = _create_markdown(md_config)
        content_html = md.convert(fm.content)
        toc = getattr(md, "toc", "")

        url = f"/{slug}/"

        return cls(
            title=title,
            slug=slug,
            content_md=fm.content,
            content_html=content_html,
            source_path=filepath,
            url=url,
            toc=toc,
            layout=layout,
        )


def _create_markdown(md_config: dict) -> markdown.Markdown:
    """Create a Markdown instance with properly resolved extension configs."""
    extensions = md_config.get("extensions", [])
    extension_configs = md_config.get("extension_configs", {})

    # Resolve YAML-style python references in extension_configs
    resolved_configs = {}
    for ext, cfg in extension_configs.items():
        resolved_cfg = {}
        for k, v in cfg.items():
            if isinstance(v, str) and v.startswith("!!python/name:"):
                # Resolve !!python/name:module.func references
                ref = v.replace("!!python/name:", "")
                parts = ref.rsplit(".", 1)
                if len(parts) == 2:
                    try:
                        mod = __import__(parts[0], fromlist=[parts[1]])
                        resolved_cfg[k] = getattr(mod, parts[1])
                    except (ImportError, AttributeError):
                        resolved_cfg[k] = v
                else:
                    resolved_cfg[k] = v
            else:
                resolved_cfg[k] = v
        resolved_configs[ext] = resolved_cfg

    return markdown.Markdown(
        extensions=extensions,
        extension_configs=resolved_configs,
    )


def _parse_date(value, filepath: Path | None = None) -> datetime:
    """Parse a date from various formats."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    # Try to extract date from filename like 2026-03-15-title.md
    if filepath:
        match = __import__("re").match(r"(\d{4}-\d{2}-\d{2})", filepath.stem)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
    return datetime.now()


def _ensure_list(value) -> list[str]:
    """Ensure value is a list of strings."""
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
