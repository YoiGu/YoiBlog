"""Preview server manager for WebUI — runs in a background thread."""

import threading
from werkzeug.serving import make_server

from ..config import Config
from ..generator import generate
from ..server import create_preview_app

_DEFAULT_PORT = 8001


class PreviewServerManager:
    """Manages a background Flask preview server."""

    def __init__(self):
        self._server = None
        self._thread = None
        self._lock = threading.Lock()
        self.port = _DEFAULT_PORT

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, config: Config, port: int = _DEFAULT_PORT) -> int:
        """Generate site and start preview server. Returns the port."""
        with self._lock:
            if self.is_running():
                return self.port

            # Generate site first
            generate(config, quiet=True)

            self.port = port
            app = create_preview_app(config)

            # Try the requested port, increment if busy
            for attempt in range(10):
                try:
                    self._server = make_server("0.0.0.0", self.port, app)
                    break
                except OSError:
                    self.port += 1
            else:
                raise RuntimeError("Could not find an available port")

            self._thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
            )
            self._thread.start()
            return self.port

    def stop(self):
        """Shutdown the preview server without blocking the caller."""
        with self._lock:
            if self._server is not None:
                server = self._server
                self._server = None
                self._thread = None
                # Run shutdown in a separate thread so the API responds immediately.
                # shutdown() blocks until serve_forever() exits its poll loop.
                threading.Thread(target=server.shutdown, daemon=True).start()


# Singleton instance shared across API calls
preview_manager = PreviewServerManager()
