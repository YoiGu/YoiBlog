<div align="center">

# YoiBlog

**A modern, full-featured static blog generator built with Python.**

Write in Markdown. Generate a beautiful, responsive blog. Deploy to GitHub Pages — all from the terminal or a built-in browser-based management UI.

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](pyproject.toml)

[简体中文](README.zh-CN.md) | English

</div>

---

## Why YoiBlog

Most static site generators ask you to choose: either a powerful CLI with no visual interface, or a heavy CMS that defeats the purpose of "static." YoiBlog takes a different approach — it gives you a clean, fast CLI for automation and scripting, while also shipping a full WebUI for when you want to manage your blog visually in the browser. No external services, no databases, no JavaScript frameworks at build time. Just Python, Markdown, and a single `pip install`.

YoiBlog is designed around a simple workflow: you write posts in Markdown with YAML front matter, run one command (or click one button) to generate a complete static site, and deploy it directly to GitHub Pages with built-in authentication support. The generated site is entirely self-contained — plain HTML, CSS, and JS files that can be hosted anywhere.

## Features

### Content & Rendering

- **Extended Markdown** — YoiBlog uses [Python-Markdown](https://python-markdown.github.io/) with the [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) suite. Out of the box, you get fenced code blocks with Pygments syntax highlighting, tables, footnotes, definition lists, abbreviations, and task lists.
- **LaTeX math formulas** — Write inline math with `$...$` and display math with `$$...$$`. Rendered client-side via [KaTeX](https://katex.org/) for fast, high-quality typesetting.
- **Rich formatting extensions** — `==highlighted text==`, `~~strikethrough~~`, `^^superscript^^`, `~subscript~`, `++keyboard shortcuts++`, `:emoji:`, and collapsible `???+ details` blocks are all supported natively.
- **Excerpt / summary control** — Each post can define a custom `excerpt` in its front matter. When provided, this text appears on the post list cards instead of the auto-generated truncation, giving you precise control over how each post is presented on the homepage.

### Site Generation

- **Paginated index** — The homepage automatically paginates posts with configurable items per page. Users can sort posts by date or title directly in the browser without a server round-trip.
- **Taxonomy pages** — Tag and category pages are generated automatically from your post metadata. Each tag and category gets its own listing page with post counts.
- **Archive page** — Posts grouped by year in reverse chronological order.
- **Full-text search** — A JSON search index is generated at build time. The default theme includes a client-side search page that queries this index instantly — no server, no API calls.
- **SEO & feeds** — Every build produces a `sitemap.xml`, `robots.txt`, RSS feed (`rss.xml`), and Atom feed (`atom.xml`).
- **Profile / About page** — A dedicated profile page with avatar, bio, social links, and post statistics, configured entirely through `_config.yml`.

### Default Theme

The bundled theme is designed to feel modern and polished without being heavy:

- **Light / dark mode** — Automatically follows the user's system preference, with a manual toggle in the header. The choice is persisted in `localStorage`.
- **Responsive layout** — Tested from 320px mobile to widescreen. The navigation collapses into a hamburger menu on small screens.
- **Reading progress bar** — A thin gradient bar at the top of the viewport shows how far the reader has scrolled through a post.
- **Floating table of contents** — On post pages, a sticky sidebar on the right displays the heading structure of the article. As the reader scrolls, the current section is highlighted in real time. On screens narrower than 1024px, the sidebar is hidden to preserve reading space.
- **Reading time estimation** — Displayed in the post header. The calculation is CJK-aware: Chinese/Japanese/Korean characters are counted at 300 characters per minute, while Latin text is counted at 200 words per minute.
- **Image lightbox** — Clicking any image in a post opens it in a full-screen overlay with backdrop blur. Press Escape or click outside to dismiss.
- **Code copy button** — Every code block gets a "Copy" button on hover, allowing readers to copy the content with one click.
- **Back-to-top button** — Appears after scrolling past 400px, smoothly scrolls back to the top.
- **Gradient accent system** — The theme uses an indigo-to-purple gradient for headings, buttons, and interactive highlights. Both light and dark modes have carefully tuned contrast.
- **Print stylesheet** — Non-essential UI elements (header, footer, TOC, progress bar) are hidden when printing.

### Bilingual Interface

When `site.language` is set to `zh` in `_config.yml`, all navigation links, page titles, sorting controls, reading time labels, pagination text, and other UI chrome are rendered in Chinese. Set it to `en` for English. This applies to the generated blog site — the WebUI has its own independent language toggle.

### WebUI

Running `yoiblog webui` launches a Flask-based management interface on `http://localhost:8080`. It provides:

- **Dashboard** — At a glance: total posts, tags, categories, current theme. A "Generate Site" button triggers a full rebuild.
- **Post editor** — A split-pane Markdown editor with live preview. The preview uses the same rendering pipeline as the generator, so what you see is what you get — including math formulas, code highlighting, and all extensions. Posts can be saved as drafts or published directly (publishing triggers an automatic site regeneration).
- **Post list** — All posts in a sortable table. Click column headers to sort by title, date, or status. Delete posts with confirmation.
- **Settings** — Configure site metadata (title, subtitle, author, URL), blog settings (theme, permalink pattern, pagination), deploy credentials (HTTPS token or SSH key with a connection test button), and profile information (avatar URL, bio, social links).
- **Deploy** — Generate the site and push to GitHub Pages in one step. The log output is displayed in real time.
- **Chinese / English switching** — Click the language button in the sidebar to toggle the entire WebUI between Chinese and English. The preference is stored in a cookie.

### Deployment

YoiBlog deploys to GitHub Pages by creating a temporary Git repository, copying the generated `public/` directory into it, committing, and force-pushing to the configured branch. This approach means your blog directory does not need to be a Git repository — no `git init` required, no conflicts with your source code repo.

Two authentication methods are supported:

- **HTTPS + Token** — Provide a GitHub Personal Access Token (with `repo` scope). The token is embedded in the remote URL during push. This is the simplest method and works behind firewalls that block SSH.
- **SSH key** — Specify the path to your SSH private key. YoiBlog sets `GIT_SSH_COMMAND` to use this key for the push.

Both can be configured through `_config.yml`, CLI flags (`--token`, `--ssh-key`), or the WebUI settings page. The "Test Connection" button in the WebUI verifies that your credentials work before you attempt a deploy.

## Installation

**Prerequisites:** Python 3.10 or later, and Git (required for deployment only).

Install directly from the repository:

```bash
pip install git+https://github.com/your-username/yoiblog.git
```

Or clone and install in development mode:

```bash
git clone https://github.com/your-username/yoiblog.git
cd yoiblog
pip install -e .
```

Verify that the CLI is available:

```bash
yoiblog --version
```

All dependencies (`Click`, `Flask`, `Jinja2`, `Markdown`, `pymdown-extensions`, `python-frontmatter`, `PyYAML`, `Pygments`, `feedgen`, `watchdog`, `colorama`) are installed automatically.

## Quick Start

### 1. Initialize a new blog

```bash
yoiblog init my-blog
cd my-blog
```

This creates the following directory structure:

```
my-blog/
├── _config.yml              # All site configuration in one file
├── .gitignore               # Ignores public/ and other generated files
└── source/
    ├── _posts/
    │   └── 2026-03-17-hello-world.md   # A sample post with demo content
    ├── _drafts/             # Draft posts (excluded from generation by default)
    └── about.md             # A standalone "About" page
```

The sample post includes examples of code blocks, task lists, tables, math formulas, highlighted text, and collapsible sections — so you can see the rendering capabilities immediately.

### 2. Create a new post

```bash
yoiblog new "Understanding Static Site Generators"
```

This generates a file like `source/_posts/2026-03-17-understanding-static-site-generators.md` with the following front matter:

```yaml
---
title: "Understanding Static Site Generators"
date: 2026-03-17 15:30:00
tags: []
categories: []
excerpt: ""
---

Write your content here in Markdown.
```

To create a draft instead (excluded from the build unless `--drafts` is passed):

```bash
yoiblog new "Work in Progress" -d
```

### 3. Generate the site

```bash
yoiblog generate
```

Output:

```
🔨 Generating site: My Blog
   Found 2 posts, 1 pages
✅ Site generated at: /path/to/my-blog/public
```

The entire site is written to the `public/` directory as static files. To include drafts in the build:

```bash
yoiblog generate --drafts
```

### 4. Preview locally

```bash
yoiblog serve
```

Opens a local server at `http://localhost:8000` with file watching enabled. When you edit a Markdown file, the site regenerates automatically and you can refresh the browser to see changes. To use a different port:

```bash
yoiblog serve -p 3000
```

### 5. Deploy to GitHub Pages

First, configure your repository and credentials in `_config.yml`:

```yaml
deploy:
  repo: "https://github.com/username/username.github.io.git"
  branch: gh-pages
  auth_method: token        # "token" or "ssh"
  github_token: "ghp_xxxxxxxxxxxx"
```

Then run:

```bash
yoiblog deploy
```

The site will be generated (if not already) and pushed to the specified branch. You can also pass credentials directly:

```bash
yoiblog deploy --token ghp_xxxxxxxxxxxx
yoiblog deploy --ssh-key ~/.ssh/id_ed25519
```

## CLI Reference

| Command | Description | Key Options |
|---|---|---|
| `yoiblog init [path]` | Scaffold a new blog at the given path (defaults to `.`) | — |
| `yoiblog new "title"` | Create a new post with the given title | `-d` / `--draft` — save to `_drafts/` |
| `yoiblog generate` | Build the static site into `public/` | `--drafts` — include draft posts |
| `yoiblog clean` | Delete the `public/` directory | — |
| `yoiblog serve` | Start a local preview server with file watching | `-p` — port (default: 8000) <br> `--no-watch` — disable auto-rebuild |
| `yoiblog deploy` | Deploy to GitHub Pages | `-m` — commit message <br> `--token` — GitHub PAT <br> `--ssh-key` — path to SSH key |
| `yoiblog webui` | Launch the browser-based management UI | `-p` — port (default: 8080) |

## Configuration Reference

The `_config.yml` file at the blog root controls all aspects of the site. Below is a complete reference:

```yaml
# === Site metadata ===
site:
  title: "My Blog"                        # Appears in the header and page titles
  subtitle: "A short tagline"             # Shown below the title on the homepage hero
  description: "A blog about technology"  # Used in meta tags and RSS feeds
  author: "Your Name"                     # Displayed in the footer and profile page
  language: zh                            # "zh" for Chinese interface, "en" for English
  url: "https://username.github.io"       # Full URL of the deployed site (used in feeds, sitemap)
  root: /                                 # URL root path

# === Blog settings ===
theme: default                            # Theme directory name
permalink: ":year/:month/:day/:slug/"     # URL pattern for posts (:year, :month, :day, :slug)

pagination:
  per_page: 10                            # Number of posts per page on the index

# === Deploy ===
deploy:
  type: github_pages
  repo: ""                                # Repository URL (HTTPS or SSH format)
  branch: gh-pages                        # Branch to push to
  cname: ""                               # Custom domain (written as CNAME file)
  auth_method: token                      # "token" or "ssh"
  github_token: ""                        # GitHub Personal Access Token
  ssh_key_path: ""                        # Absolute path to SSH private key

# === Profile / About page ===
profile:
  avatar: ""                              # URL to avatar image
  bio: ""                                 # Short bio text
  social:                                 # Social links (key: platform name, value: URL)
    github: ""
    twitter: ""
```

## Markdown Syntax Reference

In addition to standard Markdown (headings, bold, italic, links, images, lists, blockquotes, code), YoiBlog supports:

| Syntax | Result | Extension |
|---|---|---|
| `$E = mc^2$` | Inline math formula | pymdownx.arithmatex + KaTeX |
| `$$\int_0^1 x\,dx = \frac{1}{2}$$` | Display math block | pymdownx.arithmatex + KaTeX |
| `` `code` `` | Inline code | built-in |
| ```` ```python ```` | Syntax-highlighted code block | codehilite + Pygments |
| `==highlighted==` | Highlighted / marked text | pymdownx.mark |
| `~~deleted~~` | ~~Strikethrough~~ | pymdownx.tilde |
| `^^superscript^^` | Superscript text | pymdownx.caret |
| `~subscript~` | Subscript text | pymdownx.tilde |
| `++ctrl+shift+p++` | Keyboard shortcut rendering | pymdownx.keys |
| `???+ note "Title"` | Collapsible details block | pymdownx.details |
| `:emoji_name:` | Emoji rendering | pymdownx.emoji |
| `- [x] Task done` | Checkbox task list | pymdownx.tasklist |
| `[^1]: Footnote` | Footnote reference | footnotes |
| `*[abbr]: Full` | Abbreviation tooltip | abbr |
| `Term\n: Definition` | Definition list | def_list |

The Markdown extension list is configurable in `_config.yml` under the `markdown` key, but the defaults cover the vast majority of use cases.

## Theming

### Using the default theme

The default theme is bundled inside the `yoiblog` package and used automatically. No configuration needed.

### Creating a custom theme

To customize the look of your blog, create a `themes/<name>/` directory at your blog root with the following structure:

```
themes/my-theme/
├── templates/           # Jinja2 templates (base.html, index.html, post.html, etc.)
└── static/
    ├── css/             # Stylesheets
    └── js/              # JavaScript files
```

Set `theme: my-theme` in `_config.yml`. YoiBlog will use your theme directory instead of the bundled default. You can copy the default theme as a starting point and modify it from there.

### Template variables

All templates have access to the following global variables:

| Variable | Type | Description |
|---|---|---|
| `site` | object | Site config (title, subtitle, author, language, url, etc.) |
| `config` | object | Full config object including profile, deploy, etc. |
| `all_posts` | list | All published posts, sorted by date descending |
| `pages` | list | All standalone pages |
| `tags` | dict | Tag index (`{slug: {name, count, posts}}`) |
| `categories` | dict | Category index (same structure as tags) |

## Project Structure

```
yoiblog/
├── __init__.py          # Package version
├── __main__.py          # python -m yoiblog entry point
├── cli.py               # Click-based CLI (init, new, generate, serve, deploy, webui)
├── config.py            # _config.yml loading, validation, and saving
├── generator.py         # Core generation engine — loads content, renders templates, writes output
├── post.py              # Post and Page dataclasses, Markdown rendering with extension resolution
├── deployer.py          # GitHub Pages deployment via temporary git repo + force push
├── server.py            # Local HTTP server with watchdog-based file monitoring
├── scaffold.py          # Blog scaffolding (init templates, new post creation)
├── pagination.py        # Pagination logic for index pages
├── taxonomies.py        # Tag and category index building
├── feed.py              # RSS and Atom feed generation (via feedgen)
├── search_index.py      # JSON search index generation for client-side search
├── utils.py             # Shared utilities (slugify, HTML truncation, file operations)
├── scaffold_templates/  # Template files copied during `yoiblog init`
├── themes/
│   └── default/
│       ├── templates/   # 14 Jinja2 templates (base, index, post, archive, tag, etc.)
│       └── static/      # CSS, JS, and other assets
└── webui/
    ├── __init__.py      # Flask app factory with i18n context processor
    ├── api.py           # REST API (CRUD posts, generate, deploy, settings, preview)
    ├── routes.py        # Page routes (dashboard, editor, posts, settings, deploy)
    ├── i18n.py          # Complete Chinese/English translation dictionaries
    ├── static/          # WebUI-specific CSS and assets
    └── templates/       # WebUI Jinja2 templates (6 pages)
```

## License

[MIT](LICENSE)
