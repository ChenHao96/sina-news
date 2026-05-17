import sqlite3
import os
import sys
import json
import argparse

sys.stdout.reconfigure(encoding='utf-8')

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sina_news.db")

def main(key, num, size):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if size < 10:
        size = 10
        
    offset = 0
    if num > 1:
        offset = (num - 1) * size

    # 查询关键字
    cursor.execute('''
        SELECT a.oid, a.title, a.url, a.ctime, a.intro, a.media_name, b.text_content
        FROM news_detil_fts b JOIN news a ON a.oid = b.rowid
        WHERE news_detil_fts MATCH ? limit ? OFFSET ?;
    ''',(key, size, offset))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='新浪新闻库搜索')
    parser.add_argument('key', help='新闻关键字')
    parser.add_argument('-n', '--number', type=int, default=1, help='页码')
    parser.add_argument('-s', '--size', type=int, default=10, help='个数')
    args = parser.parse_args()

    main(args.key, args.number, args.size)
