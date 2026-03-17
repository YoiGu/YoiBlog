"""Local development server with live reload for YoiBlog."""

import threading
import time
from pathlib import Path

from flask import Flask, send_from_directory

from .config import Config
from .generator import generate


def create_preview_app(config: Config) -> Flask:
    """Create Flask app serving the public directory."""
    app = Flask(__name__, static_folder=None)
    public_dir = str(config.public_dir)

    @app.route("/")
    def index():
        return send_from_directory(public_dir, "index.html")

    @app.route("/<path:path>")
    def serve_file(path):
        # Try exact path first
        full_path = Path(public_dir) / path
        if full_path.is_file():
            return send_from_directory(public_dir, path)
        # Try path/index.html
        index_path = full_path / "index.html"
        if index_path.is_file():
            return send_from_directory(public_dir, f"{path}/index.html")
        # Try 404
        error_page = Path(public_dir) / "404.html"
        if error_page.exists():
            return send_from_directory(public_dir, "404.html"), 404
        return "Not Found", 404

    return app


def serve(config: Config, port: int = 8000, watch: bool = True) -> None:
    """Start the dev server with optional file watching."""
    # Generate first
    print("📦 Generating site...")
    generate(config, quiet=True)

    if watch:
        _start_watcher(config)

    print(f"🌐 Server running at http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    print()

    app = create_preview_app(config)
    app.run(host="0.0.0.0", port=port, debug=False)


def _start_watcher(config: Config) -> None:
    """Start file watcher in background thread."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        class RebuildHandler(FileSystemEventHandler):
            def __init__(self):
                self._last_rebuild = 0
                self._lock = threading.Lock()

            def on_any_event(self, event):
                if event.is_directory:
                    return
                # Debounce - wait at least 1 second between rebuilds
                now = time.time()
                with self._lock:
                    if now - self._last_rebuild < 1:
                        return
                    self._last_rebuild = now

                print(f"🔄 File changed: {event.src_path}")
                try:
                    generate(config, quiet=True)
                    print("✅ Rebuilt")
                except Exception as e:
                    print(f"❌ Rebuild failed: {e}")

        observer = Observer()
        handler = RebuildHandler()
        observer.schedule(handler, str(config.source_dir), recursive=True)

        # Also watch theme if it's in user directory
        user_theme = config.blog_root / "themes"
        if user_theme.exists():
            observer.schedule(handler, str(user_theme), recursive=True)

        observer.daemon = True
        observer.start()
        print("👁️  Watching for file changes...")
    except ImportError:
        print("⚠️  watchdog not installed, file watching disabled")
