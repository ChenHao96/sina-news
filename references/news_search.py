import asyncio
import argparse
import sys
import json as json_module
from urllib.parse import urlencode
from playwright.async_api import async_playwright

from commons import scrape_article

sys.stdout.reconfigure(encoding='utf-8')


async def search_news(browser, key, pageNum=1, size=50):
    """搜索新闻链接自动翻页过滤旧新闻"""

    if pageNum < 1:
        pageNum = 1

    if size < 10:
        size = 10

    fields = ['title', 'url', 'intro', 'ctime']

    page = await browser.new_page()
    try:
        news = []

        params = {
            'q': key,
            'page': pageNum,
            'size': size,
            'tp': 'news',
            'sort': 0,
            'from': 'search_result'
        }
        encoded_params = urlencode(params)

        api_url = f"https://search.sina.com.cn/api/news?{encoded_params}"
        response = await page.request.get(api_url)

        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            json_str = await response.text()

            data = json_module.loads(json_str)
            news_list = data.get('data', {}).get('list', [])

            if len(news_list) > 0:
                for item in news_list:
                    obj = {'media_name': item.get('media_show','')}
                    for field in fields:
                        obj.update({f'{field}': item.get(field, '')})
                    news.append(obj)

        return news
    finally:
        await page.close()


async def main(key, num=1, size=50):
    # 开启浏览器仿真
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 打开新浪新闻搜索页面，模拟获取API的验证参数
        try:
            page = await browser.new_page()
            params = {
                'q': key,
                'tp': 'news'
            }
            encoded_params = urlencode(params)
            await page.goto(f"https://search.sina.com.cn/search?{encoded_params}", wait_until="networkidle")
        except Exception as e:
            print(f"[!] 发生错误1: {type(e).__name__}: {e}")
            return

        # 搜索新闻链接列表
        news = await search_news(browser, key, num, size)

        # 新闻链接获取正文
        if len(news) > 0:
            try:
                page = await browser.new_page()
                for item in news:
                    # 访问链接抓取正文
                    _, text = await scrape_article(page, item['url'])
                    item.update({'text_content': text})
            except Exception as e:
                print(f"[!] 发生错误2: {type(e).__name__}: {e}")
                return

        print(json_module.dumps(news, ensure_ascii=False))



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='新浪新闻搜索器')
    parser.add_argument('key', help='新闻关键字')
    parser.add_argument('-n', '--number', type=int, default=1, help='页码')
    parser.add_argument('-s', '--size', type=int, default=10, help='个数')
    args = parser.parse_args()

    asyncio.run(main(args.key, args.number, args.size))
