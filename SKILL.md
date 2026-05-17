---
name: sina-news
description: 新浪新闻爬取、搜索与本地全文检索工具。
version: 1.0.0
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    requires:
      bins:
        - python
    os:
      - win32
      - darwin
      - linux
    emoji: "📰"
    envVars: []
---

# sina-news — 新浪新闻工具

基于 Playwright 的新浪新闻爬取、搜索与本地管理工具。使用 SQLite + jieba 中文分词 + FTS5 全文检索。

## 每次使用前

```bash
cd {baseDir}
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
playwright install chromium
```

## 请求到脚本映射

当收到用户的自然语言请求时，映射到下面对应的脚本执行：

| 用户意图 | 执行脚本 | 示例 |
|----------|----------|------|
| 爬取/更新/获取最新新闻 | `python {baseDir}/references/news_roll.py` |  "爬取今天的新浪新闻" |
| 搜索/查找某关键词的新浪新闻 | `python {baseDir}/references/news_search.py <keyword>` |  "搜索关于AI的新闻" |
| 查询本地已存的新闻记录 | `python {baseDir}/references/news_repository.py <keyword>` |  "查一下数据库里关于俄乌的新闻" |

### 参数说明

**search** (`news_search.py`):
- `<keyword>`: 搜索关键词（必填）
- `-n, --number`: 页码，默认 1
- `-s, --size`: 每页条数，默认 10

**query** (`news_repository.py`):
- `<keyword>`: 搜索关键词（必填）
- `-n, --number`: 页码，默认 1
- `-s, --size`: 每页条数，默认 10

## 返回值

> title: 新闻标题  
> url:  新闻链接  
> media_name: 媒体名称  
> ctime: 新闻时间(时间戳)  
> text_content: 新闻正文  
> intro: 新闻简要

**roll** (`news_roll.py`):
```json
[
  {"title": "...", "url": "...", "intro": "...", "media_name": "...", "text_content": "...", "ctime": 1778917500},
  ...
]
```

**search** (`news_search.py`):
```json
[
  {"title": "...", "url": "...", "intro": "...", "media_name": "...", "text_content": "...", "ctime": 1778917500},
  ...
]
```

**query** (`news_repository.py`):
```json
[
  {"title": "...", "url":"...", "intro": "...", "media_name": "...", "text_content": "...", "ctime": 1778917500},
  ...
]
```


## 数据文件

`sina_news.db` 位于项目根目录（`{baseDir}/sina_news.db`）。
