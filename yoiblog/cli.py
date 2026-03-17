"""CLI interface for YoiBlog."""

import shutil
import sys
from pathlib import Path

import click

from . import __version__


@click.group()
@click.version_option(__version__, prog_name="YoiBlog")
def main():
    """YoiBlog - A modern static blog generator with WebUI."""
    pass


@main.command()
@click.argument("path", default=".")
def init(path):
    """Initialize a new blog."""
    from .scaffold import init_blog
    target = Path(path).resolve()
    init_blog(target)


@main.command()
@click.argument("title")
@click.option("--draft", "-d", is_flag=True, help="Create as draft")
def new(title, draft):
    """Create a new post."""
    from .config import find_blog_root
    from .scaffold import new_post
    blog_root = find_blog_root()
    new_post(blog_root, title, draft)


@main.command()
@click.option("--drafts", is_flag=True, help="Include drafts")
def generate(drafts):
    """Generate the static site."""
    from .config import Config
    from .generator import generate as gen
    config = Config.load()
    gen(config, include_drafts=drafts)


@main.command()
def clean():
    """Clean the generated site."""
    from .config import Config
    config = Config.load()
    if config.public_dir.exists():
        shutil.rmtree(config.public_dir)
        print(f"🧹 Cleaned: {config.public_dir}")
    else:
        print("Nothing to clean.")


@main.command()
@click.option("--port", "-p", default=8000, help="Server port")
@click.option("--no-watch", is_flag=True, help="Disable file watching")
def serve(port, no_watch):
    """Start local preview server."""
    from .config import Config
    from .server import serve as start_server
    config = Config.load()
    start_server(config, port=port, watch=not no_watch)


@main.command()
@click.option("--message", "-m", default=None, help="Deploy commit message")
@click.option("--token", "-t", default=None, help="GitHub personal access token")
@click.option("--ssh-key", default=None, help="Path to SSH private key")
def deploy(message, token, ssh_key):
    """Deploy site to GitHub Pages."""
    from .config import Config
    from .deployer import deploy as do_deploy, DeployError
    config = Config.load()

    # Override auth from CLI flags
    if token:
        config.deploy.auth_method = "token"
        config.deploy.github_token = token
    if ssh_key:
        config.deploy.auth_method = "ssh"
        config.deploy.ssh_key_path = ssh_key

    try:
        do_deploy(config, message=message)
    except DeployError as e:
        print(f"❌ {e}")
        sys.exit(1)


@main.command()
@click.option("--port", "-p", default=8080, help="WebUI port")
def webui(port):
    """Launch the web management interface."""
    from .config import Config
    from .webui import create_app
    config = Config.load()
    app = create_app(config)
    print(f"🖥️  WebUI running at http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
