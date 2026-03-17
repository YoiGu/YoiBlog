"""Scaffolding for new blogs and posts."""

import shutil
from datetime import datetime
from pathlib import Path

from .utils import ensure_dir, slugify, write_file


def init_blog(target: Path) -> None:
    """Initialize a new blog at target directory."""
    scaffold_dir = Path(__file__).parent / "scaffold_templates"

    if target.exists() and any(target.iterdir()):
        print(f"⚠️  Directory {target} is not empty. Proceeding anyway...")

    # Copy scaffold templates
    _copy_scaffold(scaffold_dir, target)

    print(f"✅ Blog initialized at: {target}")
    print()
    print("Next steps:")
    print(f"  cd {target}")
    print("  yoiblog generate")
    print("  yoiblog serve")


def _copy_scaffold(src: Path, dst: Path) -> None:
    """Copy scaffold templates to target."""
    ensure_dir(dst)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            dest_file = dst / rel
            ensure_dir(dest_file.parent)
            # Handle gitignore template rename
            if item.name == "gitignore_tpl":
                content = item.read_text(encoding="utf-8")
                write_file(dest_file.with_name(".gitignore"), content)
            elif item.suffix in (".yml", ".md"):
                content = item.read_text(encoding="utf-8")
                write_file(dest_file, content)
            else:
                shutil.copy2(item, dest_file)


def new_post(blog_root: Path, title: str, draft: bool = False) -> Path:
    """Create a new post markdown file."""
    slug = slugify(title)
    date = datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"

    if draft:
        target_dir = blog_root / "source" / "_drafts"
    else:
        target_dir = blog_root / "source" / "_posts"

    ensure_dir(target_dir)
    filepath = target_dir / filename

    content = f"""---
title: "{title}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")}
tags: []
categories: []
excerpt: ""
---

Write your post content here...
"""
    write_file(filepath, content)
    status = "draft" if draft else "post"
    print(f"✅ New {status} created: {filepath}")
    return filepath
