"""Configuration loading and management for YoiBlog."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "site": {
        "title": "My Blog",
        "subtitle": "",
        "description": "A YoiBlog site",
        "author": "Author",
        "language": "en",
        "url": "",
        "root": "/",
    },
    "theme": "default",
    "permalink": ":year/:month/:day/:slug/",
    "pagination": {
        "per_page": 10,
    },
    "deploy": {
        "type": "github_pages",
        "repo": "",
        "branch": "gh-pages",
        "cname": "",
        "auth_method": "token",  # "token" or "ssh"
        "github_token": "",
        "ssh_key_path": "",
    },
    "markdown": {
        "extensions": [
            "fenced_code",
            "tables",
            "footnotes",
            "toc",
            "codehilite",
            "attr_list",
            "def_list",
            "abbr",
            "md_in_html",
            "pymdownx.tasklist",
            "pymdownx.mark",
            "pymdownx.tilde",
            "pymdownx.caret",
            "pymdownx.smartsymbols",
            "pymdownx.arithmatex",
            "pymdownx.details",
            "pymdownx.emoji",
            "pymdownx.superfences",
            "pymdownx.keys",
        ],
        "extension_configs": {
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
            },
            "toc": {
                "permalink": True,
            },
            "pymdownx.arithmatex": {
                "generic": True,
            },
            "pymdownx.emoji": {
                "emoji_index": "!!python/name:pymdownx.emoji.gemoji",
                "emoji_generator": "!!python/name:pymdownx.emoji.to_alt",
            },
            "pymdownx.tasklist": {
                "custom_checkbox": True,
            },
        },
    },
    "profile": {
        "avatar": "",
        "bio": "",
        "social": {},
    },
    "server": {
        "port": 8000,
    },
    "webui": {
        "port": 8080,
    },
}


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, returning new dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class SiteConfig:
    title: str = "My Blog"
    subtitle: str = ""
    description: str = "A YoiBlog site"
    author: str = "Author"
    language: str = "en"
    url: str = ""
    root: str = "/"


@dataclass
class DeployConfig:
    type: str = "github_pages"
    repo: str = ""
    branch: str = "gh-pages"
    cname: str = ""
    auth_method: str = "token"  # "token" or "ssh"
    github_token: str = ""
    ssh_key_path: str = ""


@dataclass
class PaginationConfig:
    per_page: int = 10


@dataclass
class ProfileConfig:
    avatar: str = ""
    bio: str = ""
    social: dict = field(default_factory=dict)


@dataclass
class Config:
    site: SiteConfig = field(default_factory=SiteConfig)
    theme: str = "default"
    permalink: str = ":year/:month/:day/:slug/"
    pagination: PaginationConfig = field(default_factory=PaginationConfig)
    deploy: DeployConfig = field(default_factory=DeployConfig)
    profile: ProfileConfig = field(default_factory=ProfileConfig)
    raw: dict = field(default_factory=dict)
    blog_root: Path = field(default_factory=lambda: Path.cwd())

    @classmethod
    def load(cls, blog_root: Path | None = None) -> "Config":
        """Load configuration from _config.yml."""
        if blog_root is None:
            blog_root = find_blog_root()
        config_path = blog_root / "_config.yml"
        user_config = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}

        merged = deep_merge(DEFAULT_CONFIG, user_config)

        site_data = merged.get("site", {})
        site = SiteConfig(**{k: v for k, v in site_data.items() if k in SiteConfig.__dataclass_fields__})

        deploy_data = merged.get("deploy", {})
        deploy = DeployConfig(**{k: v for k, v in deploy_data.items() if k in DeployConfig.__dataclass_fields__})

        pagination_data = merged.get("pagination", {})
        pagination = PaginationConfig(**{k: v for k, v in pagination_data.items() if k in PaginationConfig.__dataclass_fields__})

        profile_data = merged.get("profile", {})
        profile = ProfileConfig(**{k: v for k, v in profile_data.items() if k in ProfileConfig.__dataclass_fields__})

        return cls(
            site=site,
            theme=merged.get("theme", "default"),
            permalink=merged.get("permalink", ":year/:month/:day/:slug/"),
            pagination=pagination,
            deploy=deploy,
            profile=profile,
            raw=merged,
            blog_root=blog_root,
        )

    @property
    def source_dir(self) -> Path:
        return self.blog_root / "source"

    @property
    def posts_dir(self) -> Path:
        return self.blog_root / "source" / "_posts"

    @property
    def drafts_dir(self) -> Path:
        return self.blog_root / "source" / "_drafts"

    @property
    def public_dir(self) -> Path:
        return self.blog_root / "public"

    @property
    def theme_dir(self) -> Path:
        """Resolve theme directory: user themes first, then bundled."""
        user_theme = self.blog_root / "themes" / self.theme
        if user_theme.exists():
            return user_theme
        bundled = Path(__file__).parent / "themes" / self.theme
        if bundled.exists():
            return bundled
        raise FileNotFoundError(f"Theme '{self.theme}' not found")

    def get_markdown_config(self) -> dict:
        """Get markdown extension config."""
        return self.raw.get("markdown", DEFAULT_CONFIG["markdown"])

    def save(self) -> None:
        """Save current config to _config.yml."""
        config_path = self.blog_root / "_config.yml"
        data = {
            "site": {
                "title": self.site.title,
                "subtitle": self.site.subtitle,
                "description": self.site.description,
                "author": self.site.author,
                "language": self.site.language,
                "url": self.site.url,
                "root": self.site.root,
            },
            "theme": self.theme,
            "permalink": self.permalink,
            "pagination": {"per_page": self.pagination.per_page},
            "deploy": {
                "type": self.deploy.type,
                "repo": self.deploy.repo,
                "branch": self.deploy.branch,
                "cname": self.deploy.cname,
                "auth_method": self.deploy.auth_method,
                "github_token": self.deploy.github_token,
                "ssh_key_path": self.deploy.ssh_key_path,
            },
            "profile": {
                "avatar": self.profile.avatar,
                "bio": self.profile.bio,
                "social": self.profile.social,
            },
        }
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def find_blog_root(start: Path | None = None) -> Path:
    """Walk up from start to find _config.yml."""
    if start is None:
        start = Path.cwd()
    current = start.resolve()
    while True:
        if (current / "_config.yml").exists():
            return current
        parent = current.parent
        if parent == current:
            return start  # Fall back to start if not found
        current = parent
