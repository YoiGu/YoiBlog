"""Utility functions for YoiBlog."""

import re
import unicodedata
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def format_date(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format a datetime object."""
    return dt.strftime(fmt)


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_tree(src: Path, dst: Path) -> None:
    """Recursively copy a directory tree."""
    import shutil
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def copy_static(src: Path, dst: Path) -> None:
    """Copy static files, merging into destination."""
    import shutil
    if not src.exists():
        return
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            dest_file = dst / rel
            ensure_dir(dest_file.parent)
            shutil.copy2(item, dest_file)


def read_file(path: Path) -> str:
    """Read file contents as UTF-8."""
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    """Write content to file as UTF-8."""
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def truncate_html(html: str, max_length: int = 300) -> str:
    """Strip HTML tags and truncate to max_length chars."""
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."
