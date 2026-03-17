"""RSS/Atom feed generation for YoiBlog."""

from feedgen.feed import FeedGenerator

from .config import Config
from .post import Post
from .utils import write_file


def generate_feed(posts: list[Post], config: Config) -> None:
    """Generate RSS and Atom feeds."""
    fg = FeedGenerator()
    base_url = config.site.url.rstrip("/")

    fg.id(base_url or "https://example.com")
    fg.title(config.site.title)
    fg.subtitle(config.site.description)
    fg.author({"name": config.site.author})
    fg.link(href=base_url, rel="alternate")
    fg.link(href=f"{base_url}/atom.xml", rel="self")
    fg.language(config.site.language)

    # Add latest 20 posts
    for post in posts[:20]:
        fe = fg.add_entry()
        post_url = f"{base_url}{post.url}"
        fe.id(post_url)
        fe.title(post.title)
        fe.link(href=post_url)
        fe.description(post.excerpt)
        fe.content(post.content_html, type="html")
        fe.published(post.date.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
        if post.updated:
            fe.updated(post.updated.strftime("%Y-%m-%dT%H:%M:%S+00:00"))
        for tag in post.tags:
            fe.category(term=tag)

    # Write feeds
    output_dir = config.public_dir
    atom_content = fg.atom_str(pretty=True).decode("utf-8")
    rss_content = fg.rss_str(pretty=True).decode("utf-8")

    write_file(output_dir / "atom.xml", atom_content)
    write_file(output_dir / "rss.xml", rss_content)
