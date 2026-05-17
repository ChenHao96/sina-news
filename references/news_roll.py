import asyncio
import sqlite3
import os
import time
import json as json_module
from playwright.async_api import async_playwright
import jieba
import argparse
from commons import scrape_article

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "sina_news.db")


def tokenize(text):
    return ' '.join(jieba.cut(text))


def init_db():
    """初始化数据库"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            oid INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            ctime INTEGER NOT NULL,
            media_name TEXT,
            intro TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_detil (
            oid INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            text_content TEXT,
            html_content TEXT
        )
    """)

    # 创建 FTS5 虚拟表，指向 title 和 text_contetnt 列
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS news_detil_fts USING fts5(
            title, text_content,
            content='news_detil',
            content_rowid='oid'
        )
    ''')

    conn.commit()
    conn.close()


def query_last_news_time():
    """查询数据库最后一条新闻的时间, 没有记录就返回当日0点"""

    now = time.time()
    queryTime = now - (now % 86400)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("select ctime from news order by ctime desc limit 1")
    result = cursor.fetchone()

    if result is not None:
        queryTime = result[0]

    conn.close()
    return queryTime


def query_no_content_news():
    """查询数据库没有新闻正文的链接"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        select a.oid, a.title, a.url from news a left join news_detil b on b.oid = a.oid
        where b.title is null or length(b.title) = 0
    """)
    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results


def save_news(news):
    """保存新闻链接到数据库"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in news:
        cursor.execute("""
            INSERT INTO news(oid, title, url, intro, ctime, media_name) VALUES (?,?,?,?,?,?)
        """, (
            item['oid'],
            item['title'],
            item['url'],
            item['intro'],
            item['ctime'],
            item['media_name']
        ))

        conn.commit()

    conn.close()


def save_news_article(articles):
    """新闻正文保存到数据库"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in articles:

        oid = item['oid']
        title = item['title']
        html = item['html_content']
        text = item['text_content']

        cursor.execute(
            "INSERT INTO news_detil(oid, title, html_content, text_content) VALUES (?,?,?,?)", (oid, title, html, text))

        text = tokenize(text)
        title = tokenize(title)
        cursor.execute(
            "INSERT INTO news_detil_fts(rowid, title, text_content) VALUES (?,?,?)", (oid, title, text))

        conn.commit()

    conn.close()


async def roll_news(browser, time):
    """获取新闻链接自动翻页过滤旧新闻"""

    pageNum = 1
    page = await browser.new_page()

    field_time = 'ctime'
    fields = ['oid', 'title', 'url', 'intro', 'media_name']
    try:
        news = []
        while True:
            api_url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=50&page={pageNum}"
            response = await page.request.get(api_url)

            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                json_str = await response.text()

                data = json_module.loads(json_str)
                news_list = data.get('result', {}).get('data', [])

                if len(news_list) == 0:
                    break

            for item in news_list:

                ctime = int(item.get(field_time, 0))
                if ctime <= time:
                    break

                obj = {f'{field_time}': ctime}
                for field in fields:
                    obj.update({f'{field}': item.get(field, '')})

                news.append(obj)

            pageNum += 1

        return news
    finally:
        await page.close()


async def main(log = False, json = False):

    # 初始化数据库
    init_db()
    if log:
        print("init database.")

    # 最后一条新闻的时间
    time = query_last_news_time()
    if log:
        print(f"query last news time({time}).")

    # 开启浏览器仿真
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        if log:
            print("launch chromium browser.")

        # 打开新浪新闻滚动页面，模拟获取API的验证参数
        try:
            page = await browser.new_page()
            await page.goto("https://news.sina.com.cn/roll/", wait_until="networkidle")
            if log:
                print("goto sina news roll page.")
        except Exception as e:
            print(f"[!] 发生错误1: {type(e).__name__}: {e}")
            return

        # 获取新闻链接列表
        news = await roll_news(browser, time)
        if log:
            print(f"roll news({len(news)}).")

        # 新闻链接保存入库
        if len(news) > 0:
            save_news(news)
            if log:
                print("save news link.")

        # 查询数据库中未被获取正文的链接
        urls = query_no_content_news()

        total = len(urls)
        if log:
            print(f"query no content news({total}).")

        if total > 0:
            try:
                page = await browser.new_page()
                if log:
                    print("start scrape article.")
                for index, item in enumerate(urls):
                    if log:
                        print(f'\r进度: {index}/{total} ({index/total:.0%})', end='')
                    # 访问链接抓取正文
                    html_content, text_content = await scrape_article(page, item['url'])
                    item.update(
                        {'html_content': html_content, 'text_content': text_content})
                if log:
                    print(f'\r进度: {total}/{total} (100%)', end='')
            except Exception as e:
                print(f"[!] 发生错误2: {type(e).__name__}: {e}")
                return

            # 将新闻正文保存到数据库
            save_news_article(urls)
            if log:
                print("save news article.")

    if log:
        print("news roll finish.")

    if json:
        if len(urls) > 0:
            for item in urls:
                item.pop('html_content')
        print(json_module.dumps(urls, ensure_ascii=False))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='新浪新闻抓取器')
    parser.add_argument('-l', '--log', action='store_true', help='print log')
    parser.add_argument('-j', '--json', action='store_true', help='return json')
    args = parser.parse_args()

    asyncio.run(main(args.log, args.json))
