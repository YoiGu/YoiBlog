"""Pagination utility for YoiBlog."""

from dataclasses import dataclass
from math import ceil


@dataclass
class PaginationInfo:
    current: int
    total_pages: int
    per_page: int
    total_items: int
    prev_url: str | None = None
    next_url: str | None = None
    has_prev: bool = False
    has_next: bool = False


def paginate(items: list, per_page: int, current_page: int = 1, url_pattern: str = "/page/{page}/") -> tuple[list, PaginationInfo]:
    """Paginate a list of items.

    Returns (page_items, pagination_info).
    """
    total_items = len(items)
    total_pages = max(1, ceil(total_items / per_page))
    current_page = max(1, min(current_page, total_pages))

    start = (current_page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]

    has_prev = current_page > 1
    has_next = current_page < total_pages

    prev_url = None
    if has_prev:
        prev_url = "/" if current_page == 2 else url_pattern.format(page=current_page - 1)

    next_url = None
    if has_next:
        next_url = url_pattern.format(page=current_page + 1)

    info = PaginationInfo(
        current=current_page,
        total_pages=total_pages,
        per_page=per_page,
        total_items=total_items,
        prev_url=prev_url,
        next_url=next_url,
        has_prev=has_prev,
        has_next=has_next,
    )

    return page_items, info
