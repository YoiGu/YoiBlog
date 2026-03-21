"""WebUI page routes."""

from pathlib import Path

import frontmatter
from flask import Blueprint, render_template, current_app, request, make_response

bp = Blueprint("routes", __name__, static_folder="static", static_url_path="/static")


def _get_config():
    return current_app.config["BLOG_CONFIG"]


def _list_posts(config):
    """List all posts with metadata."""
    posts = []
    for dir_name, is_draft in [("_posts", False), ("_drafts", True)]:
        post_dir = config.source_dir / dir_name
        if not post_dir.exists():
            continue
        for f in sorted(post_dir.glob("*.md"), reverse=True):
            fm = frontmatter.load(str(f))
            posts.append({
                "filename": f.name,
                "title": fm.get("title", f.stem),
                "date": str(fm.get("date", "")),
                "tags": fm.get("tags", []),
                "categories": fm.get("categories", []),
                "draft": is_draft,
                "path": str(f),
            })
    return posts


@bp.route("/")
def dashboard():
    config = _get_config()
    posts = _list_posts(config)
    resp = make_response(render_template("dashboard.html",
                           config=config,
                           posts=posts[:10],
                           total_posts=len(posts),
                           total_tags=len(set(t for p in posts for t in p.get("tags", []))),
                           total_categories=len(set(c for p in posts for c in p.get("categories", [])))))
    _set_lang_cookie(resp)
    return resp


@bp.route("/posts")
def posts_list():
    config = _get_config()
    posts = _list_posts(config)
    resp = make_response(render_template("posts.html", config=config, posts=posts))
    _set_lang_cookie(resp)
    return resp


@bp.route("/posts/new")
def new_post():
    resp = make_response(render_template("editor.html", mode="new", post=None))
    _set_lang_cookie(resp)
    return resp


@bp.route("/posts/<path:filename>/edit")
def edit_post(filename):
    config = _get_config()
    # Sanitize filename
    safe_name = Path(filename).name
    if not safe_name or ".." in safe_name:
        return "Invalid filename", 400

    filepath = None
    for dir_name in ["_posts", "_drafts"]:
        candidate = config.source_dir / dir_name / safe_name
        if candidate.exists():
            filepath = candidate
            break

    if not filepath:
        return "Post not found", 404

    fm = frontmatter.load(str(filepath))
    post = {
        "filename": filepath.name,
        "title": fm.get("title", ""),
        "date": str(fm.get("date", "")),
        "tags": fm.get("tags", []),
        "categories": fm.get("categories", []),
        "excerpt": fm.get("excerpt", ""),
        "content": fm.content,
        "path": str(filepath),
    }
    resp = make_response(render_template("editor.html", mode="edit", post=post))
    _set_lang_cookie(resp)
    return resp


@bp.route("/settings")
def settings():
    config = _get_config()
    resp = make_response(render_template("settings.html", config=config))
    _set_lang_cookie(resp)
    return resp


@bp.route("/preview")
def preview_page():
    config = _get_config()
    resp = make_response(render_template("preview.html", config=config))
    _set_lang_cookie(resp)
    return resp


@bp.route("/deploy")
def deploy_page():
    config = _get_config()
    resp = make_response(render_template("deploy.html", config=config))
    _set_lang_cookie(resp)
    return resp


def _set_lang_cookie(resp):
    """Persist language choice in cookie if changed via query param."""
    lang = request.args.get("lang")
    if lang and lang in ("zh", "en"):
        resp.set_cookie("yoiblog_lang", lang, max_age=365 * 24 * 3600, samesite="Lax")
