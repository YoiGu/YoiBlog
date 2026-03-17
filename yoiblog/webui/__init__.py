"""WebUI application factory for YoiBlog."""

import secrets

from flask import Flask, request

from ..config import Config
from .i18n import get_translations


def create_app(config: Config | None = None) -> Flask:
    """Create the WebUI Flask application."""
    app = Flask(__name__,
                static_folder="static",
                template_folder="templates")
    app.secret_key = secrets.token_hex(32)

    if config is None:
        config = Config.load()
    app.config["BLOG_CONFIG"] = config

    @app.context_processor
    def inject_i18n():
        """Inject translation function and language into all templates."""
        lang = request.args.get("lang") or request.cookies.get("yoiblog_lang", "zh")
        translations = get_translations(lang)
        return {"t": translations, "lang": lang}

    from .routes import bp as routes_bp
    from .api import bp as api_bp
    app.register_blueprint(routes_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
