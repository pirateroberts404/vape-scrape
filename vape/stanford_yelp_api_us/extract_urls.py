import pprint
import time

import urllib.request, urllib.parse, urllib.error
import sqlite3
from bs4 import BeautifulSoup


def extract_url(yelp_url='http://www.yelp.com/biz/la-vapor-works-montebello'):
    soup = BeautifulSoup(urllib.request.urlopen(yelp_url).read(), 'lxml')
    soup = soup.body
    name=soup.find(class_='biz-page-title')
    if name is None:
        raise Exception()
    biz=soup.find(class_="biz-website")
    if biz is None:
        return ""
    url = biz.find('a')['href']
    parts = urllib.parse.urlparse(url)
    query_parts = urllib.parse.parse_qs(parts.query)
    true_url = query_parts['url'][0]
    return true_url

def main():
    db_name = 'test_us.db'
    conn = sqlite3.connect(db_name)

    c = conn.cursor()
    c2 = conn.cursor()
    for row in c.execute('SELECT yelp_id,url FROM entries WHERE true_url is NULL'):
        row = list(row)
        yelp_id=row[0]
        yelp_url = row[-1]
        true_url = extract_url(yelp_url)
        c2.execute('UPDATE entries SET true_url=? WHERE yelp_id=?', (true_url,yelp_id))
        conn.commit()
        print(yelp_id, time.ctime())
        time.sleep(1.0)


if __name__ == '__main__':
    main()
