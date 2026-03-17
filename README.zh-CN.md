<div align="center">

# YoiBlog

**基于 Python 的现代化全功能静态博客生成器。**

用 Markdown 写作，一键生成精美的响应式博客站点，直接部署到 GitHub Pages。全部操作既可以通过命令行完成，也可以在内置的浏览器管理界面中进行。

[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue.svg)](pyproject.toml)

[English](README.md) | 简体中文

</div>

---

## 为什么选择 YoiBlog

大多数静态站点生成器让你在两者之间二选一：要么是功能强大但没有可视化界面的 CLI 工具，要么是臃肿的 CMS 系统，背离了"静态"的初衷。YoiBlog 采取了不同的策略——它同时提供一个简洁高效的 CLI 用于自动化和脚本场景，以及一个完整的 WebUI 用于在浏览器中可视化地管理博客。不依赖外部服务，不需要数据库，构建时不引入前端框架。只需要 Python、Markdown，以及一条 `pip install`。

YoiBlog 围绕一个简单的工作流设计：你用 Markdown 撰写带有 YAML front matter 的文章，运行一个命令（或点一个按钮）生成完整的静态站点，然后利用内置的认证支持直接部署到 GitHub Pages。生成的站点完全自包含——纯 HTML、CSS 和 JS 文件，可以托管在任何地方。

## 功能特性

### 内容与渲染

- **扩展 Markdown** — YoiBlog 基于 [Python-Markdown](https://python-markdown.github.io/) 引擎，搭配 [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) 扩展套件。开箱即用地支持围栏代码块（Pygments 语法高亮）、表格、脚注、定义列表、缩写、任务列表等。
- **LaTeX 数学公式** — 使用 `$...$` 书写行内公式，`$$...$$` 书写独立公式块，由 [KaTeX](https://katex.org/) 在客户端渲染，速度快、排版质量高。
- **丰富的格式扩展** — `==高亮文本==`、`~~删除线~~`、`^^上标^^`、`~下标~`、`++键盘快捷键++`、`:emoji表情:`、`???+ 折叠块` 等语法均原生支持。
- **文章概要控制** — 每篇文章可以在 front matter 中定义 `excerpt` 字段作为自定义摘要。设置后，该摘要会显示在首页文章列表卡片上，替代自动截取的内容，让你精确控制每篇文章的呈现方式。

### 站点生成

- **分页首页** — 首页自动对文章进行分页，每页数量可配置。用户可以在浏览器中直接按日期或标题排序，无需服务器请求。
- **分类体系** — 标签页和分类页根据文章的元数据自动生成，每个标签和分类都有独立的文章列表页，附带文章计数。
- **归档页面** — 按年份倒序分组展示所有文章。
- **全文搜索** — 构建时生成 JSON 搜索索引，默认主题内置客户端搜索页，即时查询索引内容——不需要服务器，不需要 API 调用。
- **SEO 与订阅** — 每次构建自动生成 `sitemap.xml`、`robots.txt`、RSS 订阅 (`rss.xml`) 和 Atom 订阅 (`atom.xml`)。
- **个人简介页** — 独立的"关于"页面，展示头像、个人简介、社交链接和文章统计数据，全部通过 `_config.yml` 配置。

### 默认主题

内置主题追求现代、精致的视觉体验，同时保持轻量：

- **明暗模式** — 自动跟随用户系统偏好，导航栏提供手动切换按钮，选择持久化到 `localStorage`。
- **响应式布局** — 从 320px 手机屏幕到宽屏显示器均经过适配。导航栏在小屏幕上折叠为汉堡菜单。
- **阅读进度条** — 页面顶部的渐变色细条显示读者在文章中的滚动进度。
- **悬浮目录侧栏** — 文章页面右侧固定显示根据标题自动生成的目录结构。随着读者滚动，当前所在章节实时高亮。屏幕宽度小于 1024px 时自动隐藏，保证阅读空间。
- **阅读时间估算** — 显示在文章头部。计算方式对中日韩文字做了适配：CJK 字符按每分钟 300 字计算，拉丁文本按每分钟 200 词计算。
- **图片灯箱** — 点击文章中的任意图片，以全屏蒙层方式放大查看，带有背景模糊效果。按 Escape 键或点击外部区域关闭。
- **代码复制按钮** — 鼠标悬停时，每个代码块右上角出现"Copy"按钮，一键复制代码内容。
- **回到顶部** — 页面滚动超过 400px 后出现，点击平滑回到顶部。
- **渐变色调系统** — 主题使用靛蓝到紫色的渐变色用于标题、按钮和交互高亮，明暗模式均经过精心调色以保证对比度。
- **打印样式** — 打印时自动隐藏导航栏、页脚、目录、进度条等非必要 UI 元素。

### 中英双语界面

在 `_config.yml` 中将 `site.language` 设为 `zh` 后，生成站点的所有导航链接、页面标题、排序按钮、阅读时间标签、分页文字等 UI 元素都会以中文渲染。设为 `en` 则显示英文。此设置作用于生成的博客站点——WebUI 管理界面有独立的语言切换功能。

### WebUI 管理界面

运行 `yoiblog webui` 后会在 `http://localhost:8080` 启动一个基于 Flask 的管理界面，提供以下功能：

- **仪表盘** — 一览全局：文章总数、标签数、分类数、当前主题。提供"生成站点"按钮触发完整重建。
- **文章编辑器** — 分栏式 Markdown 编辑器，左侧编写，右侧实时预览。预览使用与生成器相同的渲染管线，所见即所得——包括数学公式、代码高亮和所有扩展语法。文章可以保存为草稿或直接发布（发布时自动触发站点重新生成）。
- **文章列表** — 所有文章以可排序的表格展示，点击列标题按标题、日期或状态排序。支持确认后删除。
- **系统设置** — 配置站点信息（标题、副标题、作者、URL）、博客设置（主题、链接格式、分页）、部署凭据（HTTPS Token 或 SSH 密钥，附带连接测试按钮）、以及个人简介信息（头像 URL、个人简介、社交链接）。
- **部署** — 一键生成站点并推送到 GitHub Pages，输出日志实时显示。
- **中英文切换** — 点击侧栏的语言按钮在中英文之间切换整个 WebUI 界面，偏好保存在 Cookie 中。

### 部署机制

YoiBlog 的部署方式是创建一个临时 Git 仓库，将生成的 `public/` 目录内容复制进去，提交，然后强制推送到配置的分支。这种方式意味着你的博客目录本身不需要是一个 Git 仓库——不需要 `git init`，不会与你的源代码仓库产生冲突。

支持两种认证方式：

- **HTTPS + Token** — 提供一个 GitHub Personal Access Token（需要 `repo` 权限）。推送时 Token 会嵌入到远程 URL 中。这是最简单的方式，在屏蔽 SSH 的防火墙环境下也能正常工作。
- **SSH 密钥** — 指定 SSH 私钥文件的路径。YoiBlog 会通过设置 `GIT_SSH_COMMAND` 来使用该密钥完成推送。

两种方式均可通过 `_config.yml`、CLI 参数（`--token`、`--ssh-key`）或 WebUI 设置页面进行配置。WebUI 中的"测试连接"按钮可以在正式部署前验证你的凭据是否有效。

## 安装

**前置要求：** Python 3.10 及以上版本，Git（仅部署时需要）。

从仓库直接安装：

```bash
pip install git+https://github.com/YoiGu/yoiblog.git
```

或克隆源码后以开发模式安装：

```bash
git clone https://github.com/YoiGu/yoiblog.git
cd yoiblog
pip install -e .
```

验证安装：

```bash
yoiblog --version
```

所有依赖项（`Click`、`Flask`、`Jinja2`、`Markdown`、`pymdown-extensions`、`python-frontmatter`、`PyYAML`、`Pygments`、`feedgen`、`watchdog`、`colorama`）会自动安装。

## 快速开始

### 1. 初始化博客

```bash
yoiblog init my-blog
cd my-blog
```

生成如下目录结构：

```
my-blog/
├── _config.yml              # 所有站点配置集中在一个文件中
├── .gitignore               # 忽略 public/ 等生成文件
└── source/
    ├── _posts/
    │   └── 2026-03-17-hello-world.md   # 一篇示例文章，包含各类语法演示
    ├── _drafts/             # 草稿目录（默认不参与生成）
    └── about.md             # 独立的"关于"页面
```

示例文章中包含代码块、任务列表、表格、数学公式、高亮文本和折叠块的用法示范，方便你直观了解渲染效果。

### 2. 撰写文章

```bash
yoiblog new "理解静态站点生成器"
```

在 `source/_posts/` 下生成如 `2026-03-17-理解静态站点生成器.md` 的文件，包含以下 front matter：

```yaml
---
title: "理解静态站点生成器"
date: 2026-03-17 15:30:00
tags: []
categories: []
excerpt: ""
---

在此用 Markdown 撰写正文。
```

创建草稿（默认不会被构建，除非传入 `--drafts` 参数）：

```bash
yoiblog new "还在写的文章" -d
```

### 3. 生成站点

```bash
yoiblog generate
```

输出：

```
🔨 Generating site: My Blog
   Found 2 posts, 1 pages
✅ Site generated at: /path/to/my-blog/public
```

整个站点以静态文件形式写入 `public/` 目录。要在生成时包含草稿：

```bash
yoiblog generate --drafts
```

### 4. 本地预览

```bash
yoiblog serve
```

在 `http://localhost:8000` 启动本地服务器，默认开启文件监听。编辑 Markdown 文件后站点会自动重新生成，刷新浏览器即可查看改动。指定其他端口：

```bash
yoiblog serve -p 3000
```

### 5. 部署到 GitHub Pages

首先在 `_config.yml` 中配置仓库和认证信息：

```yaml
deploy:
  repo: "https://github.com/username/username.github.io.git"
  branch: gh-pages
  auth_method: token        # "token" 或 "ssh"
  github_token: "ghp_xxxxxxxxxxxx"
```

然后执行：

```bash
yoiblog deploy
```

站点会被生成（如果尚未生成）并推送到指定分支。也可以通过命令行参数直接传入凭据：

```bash
yoiblog deploy --token ghp_xxxxxxxxxxxx
yoiblog deploy --ssh-key ~/.ssh/id_ed25519
```

## 命令行参考

| 命令 | 说明 | 主要选项 |
|---|---|---|
| `yoiblog init [path]` | 在指定路径初始化新博客（默认为当前目录） | — |
| `yoiblog new "标题"` | 创建一篇新文章 | `-d` / `--draft` — 保存到 `_drafts/` |
| `yoiblog generate` | 生成静态站点到 `public/` | `--drafts` — 包含草稿文章 |
| `yoiblog clean` | 删除 `public/` 目录 | — |
| `yoiblog serve` | 启动本地预览服务器，支持文件监听 | `-p` — 端口（默认 8000）<br>`--no-watch` — 禁用自动重建 |
| `yoiblog deploy` | 部署到 GitHub Pages | `-m` — 提交信息 <br> `--token` — GitHub PAT <br> `--ssh-key` — SSH 私钥路径 |
| `yoiblog webui` | 启动浏览器管理界面 | `-p` — 端口（默认 8080） |

## 配置参考

博客根目录的 `_config.yml` 控制站点的所有方面，以下是完整参考：

```yaml
# === 站点信息 ===
site:
  title: "我的博客"                       # 显示在导航栏和页面标题中
  subtitle: "一句话介绍"                   # 首页 Hero 区域的副标题
  description: "一个关于技术的博客"        # 用于 meta 标签和 RSS 订阅
  author: "你的名字"                       # 页脚和个人简介页显示
  language: zh                             # "zh" 中文界面 / "en" 英文界面
  url: "https://username.github.io"        # 部署后的完整 URL（用于订阅和站点地图）
  root: /                                  # URL 根路径

# === 博客设置 ===
theme: default                             # 主题目录名
permalink: ":year/:month/:day/:slug/"      # 文章 URL 格式 (:year, :month, :day, :slug)

pagination:
  per_page: 10                             # 首页每页显示文章数

# === 部署 ===
deploy:
  type: github_pages
  repo: ""                                 # 仓库 URL（HTTPS 或 SSH 格式）
  branch: gh-pages                         # 推送的目标分支
  cname: ""                                # 自定义域名（生成 CNAME 文件）
  auth_method: token                       # "token" 或 "ssh"
  github_token: ""                         # GitHub Personal Access Token
  ssh_key_path: ""                         # SSH 私钥的绝对路径

# === 个人简介页 ===
profile:
  avatar: ""                               # 头像图片 URL
  bio: ""                                  # 个人简介文本
  social:                                  # 社交链接（键: 平台名，值: URL）
    github: ""
    twitter: ""
```

## Markdown 语法参考

除标准 Markdown 语法（标题、加粗、斜体、链接、图片、列表、引用、代码）外，YoiBlog 还支持以下扩展：

| 语法 | 效果 | 来源 |
|---|---|---|
| `$E = mc^2$` | 行内数学公式 | pymdownx.arithmatex + KaTeX |
| `$$\int_0^1 x\,dx = \frac{1}{2}$$` | 独立数学公式块 | pymdownx.arithmatex + KaTeX |
| `` `code` `` | 行内代码 | 内置 |
| ```` ```python ```` | 带语法高亮的代码块 | codehilite + Pygments |
| `==高亮文本==` | 高亮标记 | pymdownx.mark |
| `~~删除线~~` | ~~删除线~~ | pymdownx.tilde |
| `^^上标^^` | 上标文本 | pymdownx.caret |
| `~下标~` | 下标文本 | pymdownx.tilde |
| `++ctrl+shift+p++` | 键盘快捷键渲染 | pymdownx.keys |
| `???+ note "标题"` | 可折叠内容块 | pymdownx.details |
| `:emoji_name:` | 表情符号 | pymdownx.emoji |
| `- [x] 已完成` | 复选框任务列表 | pymdownx.tasklist |
| `[^1]: 脚注内容` | 脚注引用 | footnotes |
| `*[缩写]: 全称` | 缩写提示 | abbr |
| `术语\n: 定义` | 定义列表 | def_list |

Markdown 扩展列表可在 `_config.yml` 的 `markdown` 字段下自定义配置，但默认配置已覆盖绝大多数使用场景。

## 主题系统

### 使用默认主题

默认主题打包在 `yoiblog` 包内部，自动使用，无需额外配置。

### 创建自定义主题

如果需要自定义博客外观，在博客根目录创建 `themes/<主题名>/` 目录，结构如下：

```
themes/my-theme/
├── templates/           # Jinja2 模板（base.html, index.html, post.html 等）
└── static/
    ├── css/             # 样式表
    └── js/              # JavaScript 文件
```

在 `_config.yml` 中设置 `theme: my-theme`，YoiBlog 会优先加载你的自定义主题目录，找不到时回退到内置默认主题。建议先复制默认主题作为起点再进行修改。

### 模板变量

所有模板均可访问以下全局变量：

| 变量 | 类型 | 说明 |
|---|---|---|
| `site` | object | 站点配置（title, subtitle, author, language, url 等） |
| `config` | object | 完整配置对象，包括 profile, deploy 等 |
| `all_posts` | list | 所有已发布文章，按日期倒序排列 |
| `pages` | list | 所有独立页面 |
| `tags` | dict | 标签索引（`{slug: {name, count, posts}}`） |
| `categories` | dict | 分类索引（结构与标签相同） |

## 项目结构

```
yoiblog/
├── __init__.py          # 包版本号
├── __main__.py          # python -m yoiblog 入口
├── cli.py               # 基于 Click 的 CLI（init, new, generate, serve, deploy, webui）
├── config.py            # _config.yml 加载、校验与保存
├── generator.py         # 核心生成引擎 — 加载内容、渲染模板、写入输出
├── post.py              # Post 和 Page 数据类，Markdown 渲染与扩展解析
├── deployer.py          # GitHub Pages 部署 — 临时 git 仓库 + 强制推送
├── server.py            # 本地 HTTP 服务器，基于 watchdog 的文件监听
├── scaffold.py          # 博客脚手架（init 模板和 new post 创建）
├── pagination.py        # 首页分页逻辑
├── taxonomies.py        # 标签和分类索引构建
├── feed.py              # RSS 和 Atom 订阅生成（基于 feedgen）
├── search_index.py      # JSON 搜索索引生成（用于客户端搜索）
├── utils.py             # 通用工具（slugify、HTML 截断、文件操作）
├── scaffold_templates/  # yoiblog init 时复制的模板文件
├── themes/
│   └── default/
│       ├── templates/   # 14 个 Jinja2 模板（base, index, post, archive, tag 等）
│       └── static/      # CSS、JS 及其他静态资源
└── webui/
    ├── __init__.py      # Flask 应用工厂，含 i18n 上下文处理器
    ├── api.py           # REST API（文章 CRUD、生成、部署、设置、预览）
    ├── routes.py        # 页面路由（仪表盘、编辑器、文章列表、设置、部署）
    ├── i18n.py          # 完整的中英文翻译字典
    ├── static/          # WebUI 专用 CSS 和静态资源
    └── templates/       # WebUI Jinja2 模板（6 个页面）
```

## 许可证

[MIT](LICENSE)
