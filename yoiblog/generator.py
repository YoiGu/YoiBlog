"""Core static site generation engine for YoiBlog."""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .feed import generate_feed
from .pagination import paginate
from .post import Page, Post
from .search_index import generate_search_index
from .taxonomies import build_archive, build_category_index, build_tag_index
from .utils import copy_static, ensure_dir, write_file


def generate(config: Config, include_drafts: bool = False, quiet: bool = False) -> None:
    """Generate the full static site."""
    if not quiet:
        print(f"🔨 Generating site: {config.site.title}")

    # Clean output
    if config.public_dir.exists():
        shutil.rmtree(config.public_dir)
    ensure_dir(config.public_dir)

    # Load content
    posts = _load_posts(config, include_drafts)
    pages = _load_pages(config)

    if not quiet:
        print(f"   Found {len(posts)} posts, {len(pages)} pages")

    # Build indexes
    tag_index = build_tag_index(posts)
    category_index = build_category_index(posts)
    archive = build_archive(posts)

    # Setup Jinja2 environment
    theme_dir = config.theme_dir
    template_dir = theme_dir / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )
    env.globals["site"] = config.site
    env.globals["config"] = config
    env.globals["tags"] = tag_index
    env.globals["categories"] = category_index
    env.globals["all_posts"] = posts
    env.globals["pages"] = pages

    # Register custom filters
    env.filters["date"] = _date_filter
    env.filters["excerpt"] = lambda html, l=200: __import__("yoiblog.utils", fromlist=["truncate_html"]).truncate_html(html, l)

    # Generate paginated index pages
    _generate_index(posts, config, env)

    # Generate individual post pages
    _generate_posts(posts, config, env)

    # Generate individual pages
    _generate_pages(pages, config, env)

    # Generate tag pages
    _generate_tag_pages(tag_index, config, env)

    # Generate category pages
    _generate_category_pages(category_index, config, env)

    # Generate archive page
    _generate_archive(archive, config, env)

    # Generate tags overview
    _generate_tags_overview(tag_index, config, env)

    # Generate categories overview
    _generate_categories_overview(category_index, config, env)

    # Generate search page
    _generate_search_page(config, env)

    # Generate profile page
    _generate_profile(config, env)

    # Generate 404
    _generate_404(config, env)

    # Generate feeds
    if posts:
        generate_feed(posts, config)

    # Generate search index
    generate_search_index(posts, config)

    # Generate sitemap
    _generate_sitemap(posts, pages, config)

    # Generate robots.txt
    _generate_robots(config)

    # Copy theme static assets
    theme_static = theme_dir / "static"
    if theme_static.exists():
        copy_static(theme_static, config.public_dir / "static")

    # Generate Pygments syntax highlighting CSS
    _generate_pygments_css(config)

    # Copy user source assets (images, etc.)
    _copy_source_assets(config)

    # Generate CNAME if configured
    if config.deploy.cname:
        write_file(config.public_dir / "CNAME", config.deploy.cname)

    if not quiet:
        print(f"✅ Site generated at: {config.public_dir}")


def _load_posts(config: Config, include_drafts: bool = False) -> list[Post]:
    """Load and sort all posts."""
    posts = []
    md_config = config.get_markdown_config()
    posts_dir = config.posts_dir

    if posts_dir.exists():
        for f in sorted(posts_dir.glob("*.md")):
            post = Post.from_file(f, md_config)
            post.build_url(config.permalink)
            if not post.draft or include_drafts:
                posts.append(post)

    # Include drafts directory if requested
    if include_drafts and config.drafts_dir.exists():
        for f in sorted(config.drafts_dir.glob("*.md")):
            post = Post.from_file(f, md_config)
            post.draft = True
            post.build_url(config.permalink)
            posts.append(post)

    # Sort by date descending
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def _load_pages(config: Config) -> list[Page]:
    """Load all standalone pages."""
    pages = []
    md_config = config.get_markdown_config()
    source_dir = config.source_dir

    if source_dir.exists():
        for f in source_dir.glob("*.md"):
            page = Page.from_file(f, md_config)
            pages.append(page)

    return pages


def _generate_index(posts: list[Post], config: Config, env: Environment) -> None:
    """Generate paginated index pages."""
    template = env.get_template("index.html")
    per_page = config.pagination.per_page
    total_pages = max(1, -(-len(posts) // per_page))  # ceil division

    for page_num in range(1, total_pages + 1):
        page_posts, pagination = paginate(posts, per_page, page_num)
        html = template.render(posts=page_posts, pagination=pagination, current_page="index")

        if page_num == 1:
            write_file(config.public_dir / "index.html", html)
        write_file(config.public_dir / f"page/{page_num}/index.html", html)


def _generate_posts(posts: list[Post], config: Config, env: Environment) -> None:
    """Generate individual post pages."""
    template = env.get_template("post.html")
    for i, post in enumerate(posts):
        prev_post = posts[i + 1] if i + 1 < len(posts) else None
        next_post = posts[i - 1] if i > 0 else None
        html = template.render(
            post=post,
            prev_post=prev_post,
            next_post=next_post,
            current_page="post",
        )
        output_path = config.public_dir / post.url.strip("/") / "index.html"
        write_file(output_path, html)


def _generate_pages(pages: list[Page], config: Config, env: Environment) -> None:
    """Generate standalone pages."""
    for page in pages:
        try:
            template = env.get_template(f"{page.layout}.html")
        except Exception:
            template = env.get_template("page.html")
        html = template.render(page=page, current_page=page.slug)
        output_path = config.public_dir / page.url.strip("/") / "index.html"
        write_file(output_path, html)


def _generate_tag_pages(tag_index: dict, config: Config, env: Environment) -> None:
    """Generate individual tag pages."""
    template = env.get_template("tag.html")
    for slug, item in tag_index.items():
        html = template.render(tag=item, current_page="tags")
        write_file(config.public_dir / f"tags/{slug}/index.html", html)


def _generate_category_pages(category_index: dict, config: Config, env: Environment) -> None:
    """Generate individual category pages."""
    template = env.get_template("category.html")
    for slug, item in category_index.items():
        html = template.render(category=item, current_page="categories")
        write_file(config.public_dir / f"categories/{slug}/index.html", html)


def _generate_archive(archive: dict, config: Config, env: Environment) -> None:
    """Generate archive page."""
    template = env.get_template("archive.html")
    html = template.render(archive=archive, current_page="archive")
    write_file(config.public_dir / "archive/index.html", html)


def _generate_tags_overview(tag_index: dict, config: Config, env: Environment) -> None:
    """Generate tags overview page."""
    template = env.get_template("tags.html")
    html = template.render(tags=tag_index, current_page="tags")
    write_file(config.public_dir / "tags/index.html", html)


def _generate_categories_overview(category_index: dict, config: Config, env: Environment) -> None:
    """Generate categories overview page."""
    template = env.get_template("categories.html")
    html = template.render(categories=category_index, current_page="categories")
    write_file(config.public_dir / "categories/index.html", html)


def _generate_search_page(config: Config, env: Environment) -> None:
    """Generate client-side search page."""
    template = env.get_template("search.html")
    html = template.render(current_page="search")
    write_file(config.public_dir / "search/index.html", html)


def _generate_profile(config: Config, env: Environment) -> None:
    """Generate profile/about page."""
    template = env.get_template("profile.html")
    html = template.render(current_page="profile")
    write_file(config.public_dir / "profile/index.html", html)


def _generate_404(config: Config, env: Environment) -> None:
    """Generate 404 page."""
    template = env.get_template("404.html")
    html = template.render(current_page="404")
    write_file(config.public_dir / "404.html", html)


def _generate_sitemap(posts: list[Post], pages: list[Page], config: Config) -> None:
    """Generate sitemap.xml."""
    base_url = config.site.url.rstrip("/")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Home
    lines.append(f"  <url><loc>{base_url}/</loc><priority>1.0</priority></url>")

    # Posts
    for post in posts:
        date_str = post.date.strftime("%Y-%m-%d")
        lines.append(f"  <url><loc>{base_url}{post.url}</loc><lastmod>{date_str}</lastmod><priority>0.8</priority></url>")

    # Pages
    for page in pages:
        lines.append(f"  <url><loc>{base_url}{page.url}</loc><priority>0.6</priority></url>")

    lines.append("</urlset>")
    write_file(config.public_dir / "sitemap.xml", "\n".join(lines))


def _generate_robots(config: Config) -> None:
    """Generate robots.txt."""
    base_url = config.site.url.rstrip("/")
    content = f"""User-agent: *
Allow: /
Sitemap: {base_url}/sitemap.xml
"""
    write_file(config.public_dir / "robots.txt", content)


def _copy_source_assets(config: Config) -> None:
    """Copy non-markdown files from source to public."""
    source = config.source_dir
    if not source.exists():
        return
    for item in source.rglob("*"):
        if item.is_file() and item.suffix != ".md" and "_posts" not in item.parts and "_drafts" not in item.parts:
            rel = item.relative_to(source)
            dest = config.public_dir / rel
            ensure_dir(dest.parent)
            shutil.copy2(item, dest)


def _generate_pygments_css(config: Config) -> None:
    """Generate Pygments syntax highlighting CSS for code blocks."""
    try:
        from pygments.formatters import HtmlFormatter
        # Light theme
        light_css = HtmlFormatter(style="default", cssclass="highlight").get_style_defs()
        # Dark theme overrides
        dark_css = HtmlFormatter(style="monokai", cssclass="highlight").get_style_defs()
        dark_css = "\n".join(
            f"[data-theme=\"dark\"] {line}" if line.strip().startswith(".highlight")
            else line
            for line in dark_css.splitlines()
        )
        css = f"/* Pygments Syntax Highlighting — auto-generated */\n{light_css}\n\n{dark_css}\n"
        css_path = config.public_dir / "static" / "css" / "highlight.css"
        ensure_dir(css_path.parent)
        write_file(css_path, css)
    except ImportError:
        pass


def _date_filter(value, fmt="%B %d, %Y"):
    """Jinja2 date filter."""
    if hasattr(value, "strftime"):
        return value.strftime(fmt)
    return str(value)
