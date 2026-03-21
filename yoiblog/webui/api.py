"""WebUI JSON API endpoints."""

import threading
from datetime import datetime
from pathlib import Path

import frontmatter
from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("api", __name__)


def _get_config():
    return current_app.config["BLOG_CONFIG"]


def _safe_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal."""
    name = Path(filename).name  # Strip any directory components
    if not name or name.startswith(".") or ".." in name:
        raise ValueError("Invalid filename")
    return name


@bp.route("/posts", methods=["GET"])
def list_posts():
    config = _get_config()
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
                "excerpt": fm.get("excerpt", ""),
                "draft": is_draft,
            })
    return jsonify(posts)


@bp.route("/posts", methods=["POST"])
def create_post():
    data = request.json
    config = _get_config()

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    content = data.get("content", "")
    tags = _parse_list_field(data.get("tags", []))
    categories = _parse_list_field(data.get("categories", []))
    is_draft = data.get("draft", False)
    auto_generate = data.get("auto_generate", False)

    from ..utils import slugify
    slug = slugify(title)
    if not slug:
        slug = "untitled"
    date = datetime.now()
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"

    dir_name = "_drafts" if is_draft else "_posts"
    target_dir = config.source_dir / dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    excerpt = data.get("excerpt", "").strip()

    post = frontmatter.Post(content)
    post["title"] = title
    post["date"] = date.strftime("%Y-%m-%d %H:%M:%S")
    post["tags"] = tags
    post["categories"] = categories
    if excerpt:
        post["excerpt"] = excerpt

    filepath = target_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    result = {"success": True, "filename": filename}

    # Auto-generate site when publishing (not drafting)
    if auto_generate and not is_draft:
        try:
            from ..generator import generate
            generate(config, quiet=True)
            result["generated"] = True
        except Exception as e:
            result["generated"] = False
            result["generate_error"] = str(e)

    return jsonify(result)


@bp.route("/posts/<path:filename>", methods=["PUT"])
def update_post(filename):
    try:
        filename = _safe_filename(filename)
    except ValueError:
        return jsonify({"error": "Invalid filename"}), 400

    data = request.json
    config = _get_config()

    # Find the file
    filepath = None
    for dir_name in ["_posts", "_drafts"]:
        candidate = config.source_dir / dir_name / filename
        if candidate.exists():
            filepath = candidate
            break

    if not filepath:
        return jsonify({"error": "Post not found"}), 404

    fm = frontmatter.load(str(filepath))

    if "title" in data:
        fm["title"] = data["title"].strip()
    if "content" in data:
        fm.content = data["content"]
    if "tags" in data:
        fm["tags"] = _parse_list_field(data["tags"])
    if "categories" in data:
        fm["categories"] = _parse_list_field(data["categories"])
    if "excerpt" in data:
        excerpt = data["excerpt"].strip()
        if excerpt:
            fm["excerpt"] = excerpt
        elif "excerpt" in fm.metadata:
            del fm.metadata["excerpt"]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(fm))

    result = {"success": True}

    # Auto-generate if requested
    auto_generate = data.get("auto_generate", False)
    is_draft = data.get("draft", False)
    if auto_generate and not is_draft:
        try:
            from ..generator import generate
            generate(config, quiet=True)
            result["generated"] = True
        except Exception as e:
            result["generated"] = False
            result["generate_error"] = str(e)

    return jsonify(result)


@bp.route("/posts/<path:filename>", methods=["DELETE"])
def delete_post(filename):
    try:
        filename = _safe_filename(filename)
    except ValueError:
        return jsonify({"error": "Invalid filename"}), 400

    config = _get_config()
    for dir_name in ["_posts", "_drafts"]:
        candidate = config.source_dir / dir_name / filename
        if candidate.exists():
            candidate.unlink()
            return jsonify({"success": True})
    return jsonify({"error": "Post not found"}), 404


@bp.route("/generate", methods=["POST"])
def trigger_generate():
    config = _get_config()
    try:
        from ..generator import generate
        generate(config)
        return jsonify({"success": True, "message": "Site generated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/deploy", methods=["POST"])
def trigger_deploy():
    config = _get_config()
    try:
        from ..deployer import deploy, DeployError
        log = deploy(config)
        return jsonify({"success": True, "message": "Deploy complete", "log": log})
    except DeployError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/deploy/test", methods=["POST"])
def test_deploy_connection():
    """Test git connection without deploying."""
    config = _get_config()
    try:
        from ..deployer import test_connection, DeployError
        msg = test_connection(config)
        return jsonify({"success": True, "message": msg})
    except DeployError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/settings", methods=["GET"])
def get_settings():
    config = _get_config()
    return jsonify({
        "site": {
            "title": config.site.title,
            "subtitle": config.site.subtitle,
            "description": config.site.description,
            "author": config.site.author,
            "language": config.site.language,
            "url": config.site.url,
        },
        "theme": config.theme,
        "permalink": config.permalink,
        "pagination": {"per_page": config.pagination.per_page},
        "deploy": {
            "repo": config.deploy.repo,
            "branch": config.deploy.branch,
            "cname": config.deploy.cname,
            "auth_method": config.deploy.auth_method,
            "github_token": config.deploy.github_token,
            "ssh_key_path": config.deploy.ssh_key_path,
        },
        "profile": {
            "avatar": config.profile.avatar,
            "bio": config.profile.bio,
            "social": config.profile.social,
        },
    })


@bp.route("/settings", methods=["POST"])
def save_settings():
    data = request.json
    config = _get_config()

    if "site" in data:
        s = data["site"]
        if "title" in s: config.site.title = s["title"]
        if "subtitle" in s: config.site.subtitle = s["subtitle"]
        if "description" in s: config.site.description = s["description"]
        if "author" in s: config.site.author = s["author"]
        if "language" in s: config.site.language = s["language"]
        if "url" in s: config.site.url = s["url"]
    if "theme" in data:
        config.theme = data["theme"]
    if "permalink" in data:
        config.permalink = data["permalink"]
    if "pagination" in data and "per_page" in data["pagination"]:
        config.pagination.per_page = int(data["pagination"]["per_page"])
    if "deploy" in data:
        d = data["deploy"]
        if "repo" in d: config.deploy.repo = d["repo"]
        if "branch" in d: config.deploy.branch = d["branch"]
        if "cname" in d: config.deploy.cname = d["cname"]
        if "auth_method" in d: config.deploy.auth_method = d["auth_method"]
        if "github_token" in d: config.deploy.github_token = d["github_token"]
        if "ssh_key_path" in d: config.deploy.ssh_key_path = d["ssh_key_path"]
    if "profile" in data:
        p = data["profile"]
        if "avatar" in p: config.profile.avatar = p["avatar"]
        if "bio" in p: config.profile.bio = p["bio"]
        if "social" in p: config.profile.social = p["social"]

    config.save()
    return jsonify({"success": True, "message": "Settings saved"})


@bp.route("/preview/start", methods=["POST"])
def preview_start():
    """Start the preview server in a background thread."""
    config = _get_config()
    from .preview_server import preview_manager
    try:
        port = preview_manager.start(config)
        return jsonify({"success": True, "port": port, "url": f"http://localhost:{port}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/preview/stop", methods=["POST"])
def preview_stop():
    """Stop the preview server."""
    from .preview_server import preview_manager
    preview_manager.stop()
    return jsonify({"success": True})


@bp.route("/preview/status", methods=["GET"])
def preview_status():
    """Check if preview server is running."""
    from .preview_server import preview_manager
    running = preview_manager.is_running()
    return jsonify({
        "running": running,
        "port": preview_manager.port if running else None,
        "url": f"http://localhost:{preview_manager.port}" if running else None,
    })


@bp.route("/preview/rebuild", methods=["POST"])
def preview_rebuild():
    """Rebuild the site (regenerate) while preview server is running."""
    config = _get_config()
    try:
        from ..generator import generate
        generate(config, quiet=True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/preview/render", methods=["POST"])
def preview_render():
    """Render markdown to HTML for live preview, using the full markdown config."""
    data = request.json
    content = data.get("content", "")
    config = _get_config()
    md_config = config.get_markdown_config()
    from ..post import _create_markdown
    md = _create_markdown(md_config)
    html = md.convert(content)
    return jsonify({"html": html})


@bp.route("/preview/highlight.css", methods=["GET"])
def preview_highlight_css():
    """Serve Pygments syntax highlighting CSS for the editor preview."""
    try:
        from pygments.formatters import HtmlFormatter
        from flask import Response
        light = HtmlFormatter(style="default", cssclass="highlight").get_style_defs()
        dark_lines = HtmlFormatter(style="monokai", cssclass="highlight").get_style_defs()
        dark = "\n".join(
            f"[data-theme=\"dark\"] {line}" if line.strip().startswith(".highlight")
            else line
            for line in dark_lines.splitlines()
        )
        css = f"{light}\n\n{dark}\n"
        return Response(css, mimetype="text/css")
    except ImportError:
        return Response("", mimetype="text/css")


def _parse_list_field(value) -> list[str]:
    """Parse tags/categories from either list or comma-separated string."""
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []
