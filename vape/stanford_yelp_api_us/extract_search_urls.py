import pprint
import string

import urllib.request, urllib.parse, urllib.error
import sqlite3

from bs4 import BeautifulSoup


def extract_all(yelp_id="certified-vaporz-lodi-2"):
    yelp_url = "http://www.yelp.com/biz/{}".format(yelp_id)
    soup = BeautifulSoup(urllib.request.urlopen(yelp_url).read(), "lxml")
    soup = soup.body

    name=soup.find(class_='biz-page-title')
    if name is None:
        raise Exception()

    name = name.string.strip()

    phone=soup.find(itemprop="telephone")
    if phone is None:
        phone = ""
    else:
        phone = phone.string.strip()
        phone = [char for char in phone if char in string.digits]
        phone = ''.join(phone)

    address=soup.find(itemprop="streetAddress")
    address_line1 = ""
    address_line2 = ""
    address_line3 = ""
    if address is not None:
        address = list(address.strings)
        if len(address) > 0:
            address_line1 = address[0]
        if len(address) > 1:
            address_line2 = address[1]
        if len(address) > 2:
            address_line3 = address[2]
        if len(address) > 3:
            print("longer addresses needed")

    city=soup.find(itemprop="addressLocality")
    if city is None:
        city = ""
    else:
        city = city.string

    postal_code=soup.find(itemprop="postalCode")
    if postal_code is None:
        postal_code = ""
    else:
        postal_code = postal_code.string

    state_code=soup.find(itemprop="addressRegion")
    if state_code is None:
        state_code = ""
    else:
        state_code = state_code.string

    is_closed = soup.find(class_="i-perm-closed-alert-biz_details")
    if is_closed is None:
        is_closed = 0
    else:
        is_closed = 1

    review_count=soup.find(class_="biz-main-info")
    review_count=review_count.find(itemprop="reviewCount")
    if review_count is None:
        review_count = 0
    else:
        review_count = int(review_count.string)

    rating=soup.find(class_="biz-main-info")
    rating=rating.find(itemprop="ratingValue")
    if rating is None:
        rating = ""
    else:
        rating = float(rating['content'])

    categories = soup.find(class_="category-str-list")
    if categories is not None:
        cats = categories.find_all('a')
        store_types = ",".join(cat.string for cat in cats)

    url=soup.find(class_="biz-website")
    if url is None:
        url = ""
    else:
        url = url.find('a')['href']
        parts = urllib.parse.urlparse(url)
        query_parts = urllib.parse.parse_qs(parts.query)
        url = query_parts['url'][0]

    return (yelp_id,name,phone,address_line1, address_line2,address_line3,city,postal_code,state_code,is_closed,review_count,rating,store_types,url)

def main():
    db_name = 'test_us.db'
    conn = sqlite3.connect(db_name)

    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c2 = conn.cursor()
    for row in c.execute('SELECT * FROM search_names WHERE yelp_id NOT IN (SELECT yelp_id FROM entries) AND yelp_id NOT IN (SELECT yelp_id FROM search_entries);'):
        row = list(row)
        yelp_id=row[0]
#        yelp_id=yelp_id.split('?')[0]
        print(yelp_id)
        query = extract_all(yelp_id)
        c2.execute('INSERT OR IGNORE INTO search_entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', query)
        conn.commit()
        print(yelp_id, time.ctime())
#        time.sleep(1)


if __name__ == '__main__':
    main()
