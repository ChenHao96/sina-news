import time
import random

async def scrape_article(page, url):
    """获取新闻链接的正文(html),纯文本"""

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        time.sleep(random.uniform(0.5, 1.0))
    except Exception as e:
        print(f"[!] 页面加载失败: {url} - {e}")
        return ""

    try:
        result = await page.evaluate("""() => {
            const artibody = document.body.querySelector("div.article[id^=arti]");
            if (!artibody) return {'content':'','text':''};
            const clone = artibody.cloneNode(true);
            if (clone.children.length > 0) {
                const query = 'script, style, blockquote, div.clearfix, div.appendQr_wrap, div.ct_hqimg, div.article-notice, p.article-editor'
                + ', div[class^=otherContent], p[class^=finance_web], div[class*=kaihu], div[style*=clear]'
                + ', div[class^=weibo]';
                clone.querySelectorAll(query).forEach(el => el.remove());
                let result = '';
                Array.from(clone.children).forEach(el => {result += el.outerHTML});
                const text = clone.innerText.trim();
                return {'content':result,'text':text};                  
            } else {
                let result = clone.textContent.trim();
                return {'content':result,'text':result};
            }
        }""")

        return result['content'], result['text']
    except Exception as e:
        print(f"[!] 文章处理失败: {url[:60]} - {e}")
        return "", ""