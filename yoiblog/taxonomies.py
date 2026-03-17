"""Tag and category taxonomy building for YoiBlog."""

from collections import defaultdict
from dataclasses import dataclass, field

from .post import Post
from .utils import slugify


@dataclass
class TaxonomyItem:
    name: str
    slug: str
    posts: list[Post] = field(default_factory=list)
    count: int = 0


def build_tag_index(posts: list[Post]) -> dict[str, TaxonomyItem]:
    """Build a tag -> posts index."""
    tags: dict[str, TaxonomyItem] = {}
    for post in posts:
        for tag in post.tags:
            slug = slugify(tag)
            if slug not in tags:
                tags[slug] = TaxonomyItem(name=tag, slug=slug)
            tags[slug].posts.append(post)
            tags[slug].count = len(tags[slug].posts)
    return dict(sorted(tags.items(), key=lambda x: x[1].count, reverse=True))


def build_category_index(posts: list[Post]) -> dict[str, TaxonomyItem]:
    """Build a category -> posts index."""
    categories: dict[str, TaxonomyItem] = {}
    for post in posts:
        for cat in post.categories:
            slug = slugify(cat)
            if slug not in categories:
                categories[slug] = TaxonomyItem(name=cat, slug=slug)
            categories[slug].posts.append(post)
            categories[slug].count = len(categories[slug].posts)
    return dict(sorted(categories.items(), key=lambda x: x[1].count, reverse=True))


def build_archive(posts: list[Post]) -> dict[int, list[Post]]:
    """Build a year -> posts archive."""
    archive: dict[int, list[Post]] = defaultdict(list)
    for post in posts:
        archive[post.date.year].append(post)
    return dict(sorted(archive.items(), reverse=True))
