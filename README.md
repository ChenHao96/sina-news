# sina-news 📰

基于 Playwright 的新浪新闻爬取、搜索与本地管理工具。使用 SQLite + jieba 中文分词 + FTS5 全文检索。

## 功能

- **新闻爬取** — 自动抓取新浪新闻首页内容，包含标题、正文、来源、发布时间
- **全文搜索** — 通过新浪站内搜索获取新闻，支持分页
- **本地检索** — 对已存入数据库的新闻进行本地全文检索
- **增量存储** — 自动去重，避免重复入库

## 快速开始

```bash
# 创建虚拟环境
python -m venv .venv
# Windows
source .venv/Scripts/activate
# macOS / Linux
# source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Chromium（Playwright 依赖）
playwright install chromium
```

## 使用方式

### 爬取最新新闻

```bash
python references/news_roll.py
```

从新浪新闻首页抓取最新文章并存入 SQLite 数据库。

### 搜索新闻

```bash
python references/news_search.py <关键词> [-n 页码] [-s 每页条数]
```

示例：

```bash
python references/news_search.py 人工智能 -n 1 -s 10
```

### 查询本地数据

```bash
python references/news_repository.py <关键词> [-n 页码] [-s 每页条数]
```

示例：

```bash
python references/news_repository.py 俄乌 -n 1 -s 10
```

## 数据输出格式

```json
{
  "title":        "新闻标题",
  "url":          "新闻链接",
  "intro":        "新闻简介",
  "media_name":   "来源媒体",
  "text_content": "新闻正文",
  "ctime":        1778917500
}
```

## 项目结构

```
sina-news/
├── references/
│   ├── commons.py          # 通用工具（正文摘取）
│   ├── news_roll.py        # 新闻爬取脚本
│   ├── news_search.py      # 新闻搜索脚本
│   └── news_repository.py  # 本地数据查询脚本
├── requirements.txt        # Python 依赖
├── sina_news.db            # SQLite 数据库（自动生成）
└── SKILL.md                # Claude Code skill 定义
```

## 技术栈

- **Playwright** — 浏览器自动化，用于新闻爬取
- **SQLite + FTS5** — 本地存储与全文检索
- **jieba** — 中文分词
- **Pyee** — CLI 交互框架
