import json
import pprint
import time
import argparse

import urllib.request, urllib.parse, urllib.error
import sqlite3

from bs4 import BeautifulSoup


def extract_search_names_zip(zip_code):
    final_names = []
    start = 0
    while True:
        search_url = "http://www.yelp.com/search/snippet?find_desc&start={}&sortby=review_count&cflt=vapeshops&find_loc={}".format(start,zip_code)
        #request = urllib2.Request(search_url)
        #request.add_header('User-Agent:','Mozilla/5.0 (compatible; ScoutJet;  http://www.scoutjet.com/)')
        #opener = urllib2.build_opener()
        #conn = opener.open(request)
        conn = urllib.request.urlopen(search_url, None)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()

        try:
            time.sleep(1)
            soup = BeautifulSoup(response['search_results'], "lxml")
            names=soup.select(".natural-search-result .biz-name")
            if len(names) == 0:
                break
            for name in names:
                final_names.append((name['href'][5:],))
            start += 10
        except:
            break

    return final_names


def main():
    db_name = 'test_us.db'
    conn = sqlite3.connect(db_name)

    parser = argparse.ArgumentParser()
    parser.add_argument('zip_code_list')
    args = parser.parse_args()

    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    with open(args.zip_code_list) as f:
        for line in f:
            zip_code = line.strip()
            names=extract_search_names_zip(zip_code)
            c.executemany('INSERT OR IGNORE INTO search_names VALUES (?)', names)
            conn.commit()
            print('zip', zip_code)

if __name__ == '__main__':
    main()
