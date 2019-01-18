# -*- coding: utf-8 -*-
import sys
import time
import pprint
import argparse

import requests
import urllib.request, urllib.parse, urllib.error
import sqlite3
import oauth2

from bs4 import BeautifulSoup
from urllib.parse import quote


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= '1a7xzG961cBpbKfmDRTS_AokAQF-10W5SwchHiZzT3WJWq-viXM_e3wgAXts864GOj3tNCfpBQ9jjCxuLYExEWRblymrX_7BAZAG63B9vvt2Zjl5zk36H_BPkqkVW3Yx'
#API_KEY= '1A3iAaux2RQvPV3ALkZRF9PZM_Lgpknq6D3mBG6MZ71WCpCQXeCBBoTultbx75blB264yOwcYehFtMzOgi7KLQZedXaGhSAS6C9wiiCu2DrMcR7swFT2-_p77o07W3Yx'
#API_KEY= 'WgU7BVVWKe3IJhTfPvH2Fgoxo15gDw4w6mj-IGikmGbdQGN6MpSaT4Uo9jnmkkEobKdaRFRA12cahSPI7PNtfn5I0ZUVxHTH0CP9m4hC3Btk8ZRf2YIevWcuCd07W3Yx'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

#    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search_category(category, location, offset=0, sort="distance"):
    """Query the Search API by a category and location.

    Args:
        category (str): The category passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'categories': category.replace(' ', ','),
        'location': location.replace(' ', '+'),
        'sort_by':  sort,
        'limit': 50,
        'radius': 40000,
        'offset': offset
    }
    time.sleep(1.6)
    return request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)

def query_api_category(category, location, sort):
    """Queries the API by the input values from the user.

    Args:
        category (str): The category to query.
        location (str): The location of the business to query.
    """

    offset = 0
    response = search_category(category, location, offset, sort)
#    pprint.pprint(response, indent=2)

    if response.get('error'):
        print(response)
        if response['error']['code'] == 'LOCATION_NOT_FOUND':
            return [], {'center': {'longitude': 0.0, 'latitude': 0.0}}
        if response['error']['code'] == 'INTERNAL_ERROR':
            time.sleep(10.0)
            response = search_category(category, location, offset, sort)
    businesses = response.get('businesses')
    region = response.get('region')

    num_businesses = response.get('total')
#    print len(businesses), num_businesses

    num_retrieved = len(businesses)

    while num_retrieved < num_businesses:
        print("Retrieved {} of {}".format(num_retrieved, num_businesses))
        offset += 50
        response = search_category(category, location, offset, sort)
        if response.get('error'):
            print(response)
            if response['error']['code'] == 'INTERNAL_ERROR':
                time.sleep(10.0)
                response = search_category(category, location, offset, sort)
        nbusinesses = response.get('businesses')
        businesses.extend(nbusinesses)
        #print len(businesses), num_businesses
        if num_retrieved == len(businesses):
            break
        num_retrieved = len(businesses)


    return businesses, region

# u'categories': [ [u'Vape Shops', u'vapeshops'],
#                                      [u'Local Services', u'localservices'],
#                                      [u'Tobacco Shops', u'tobaccoshops']],
#                     u'display_phone': u'+1-323-712-0044',
#                     u'id': u'la-vapor-works-montebello',
#                     u'image_url': u'http://s3-media1.fl.yelpassets.com/bphoto/wca0tbaQnYD7QbCimE4qJw/ms.jpg',
#                     u'is_claimed': True,
#                     u'is_closed': False,
#                     u'location': { u'address': [u'524 N Montebello Blvd'],
#                                    u'city': u'Montebello',
#                                    u'coordinate': { u'latitude': 34.0179754793644,
#                                                     u'longitude': -118.10572899878},
#                                    u'country_code': u'US',
#                                    u'display_address': [ u'524 N Montebello Blvd',
#                                                          u'Montebello, CA 90640'],
#                                    u'geo_accuracy': 8.0,
#                                    u'postal_code': u'90640',
#                                    u'state_code': u'CA'},
#                     u'mobile_url': u'http://m.yelp.com/biz/la-vapor-works-montebello',
#                     u'name': u'LA Vapor Works',
#                     u'phone': u'3237120044',
#                     u'rating': 5.0,
#                     u'rating_img_url': u'http://s3-media1.fl.yelpassets.com/assets/2/www/img/f1def11e4e79/ico/stars/v1/stars_5.png',
#                     u'rating_img_url_large': u'http://s3-media3.fl.yelpassets.com/assets/2/www/img/22affc4e6c38/ico/stars/v1/stars_large_5.png',
#                     u'rating_img_url_small': u'http://s3-media1.fl.yelpassets.com/assets/2/www/img/c7623205d5cd/ico/stars/v1/stars_small_5.png',
#                     u'review_count': 67,
#                     u'snippet_image_url': u'http://s3-media3.fl.yelpassets.com/photo/WHYFZ2KReThfHf4jlJiy3A/ms.jpg',
#                     u'snippet_text': u'100% satisfied with products & customer service. I never come out of this place disappointed. \n\nI came across this place after doing some research on yelp...',
#                     u'url': u'http://www.yelp.com/biz/la-vapor-works-montebello'}

def main():
    us_states_and_territories = set(('AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO',
                                     'CT', 'DK', 'DE', 'DC', 'FL', 'GA', 'GU',
                                     'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
                                     'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
                                     'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
                                     'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR',
                                     'OL', 'PA', 'PI', 'PR', 'RI', 'SC', 'SD',
                                     'TN', 'TX', 'UT', 'VT', 'VI', 'VA', 'WA',
                                     'WV', 'WI', 'WY'))

    parser = argparse.ArgumentParser()
    parser.add_argument('zip_code_list')
    args = parser.parse_args()
    
    state_codes = us_states_and_territories

    state_code_sql = ','.join(["'"+state+"'" for state in state_codes])

    conn = sqlite3.connect('test_us.db')

    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    category='vapeshops'

    with open(args.zip_code_list) as f:
        for line in f:
            zip_code = line.strip()
            try:
                #for sort in ('distance','best_match'):
                for sort in ('distance',):
                    businesses,region=query_api_category(category, zip_code, sort)
                    print(zip_code, sort)

                    queries = []
                    for business in businesses:
                        address_line1 = ""
                        address_line2 = ""
                        address_line3 = ""
                        city = ""
                        postal_code = ""
                        state_code = ""
                        if 'location' in business:
                            if 'address1' in business['location']:
                                address_line1 = business['location']['address1']
                            if 'address2' in business['location']:
                                address_line2 = business['location']['address2']
                            if 'address3' in business['location']:
                                address_line3 = business['location']['address3']
                            if 'city' in business['location']:
                                city = business['location']['city']
                            if 'zip_code' in business['location']:
                                postal_code = business['location']['zip_code']
                            if 'state' in business['location']:
                                state_code = business['location']['state']

                        if 'categories' in business:
                            categories = business['categories']
                            store_types = ",".join(cat['title'] for cat in categories)

                        business_id =""
                        if 'alias' in business:
                            business_id = business['alias']

                        business_name =""
                        if 'name' in business:
                            business_name = business['name']

                        business_phone =""
                        if 'phone' in business:
                            business_phone = business['phone']

                        is_closed =""
                        if 'is_closed' in business:
                            is_closed = int(business['is_closed'])

                        review_count =""
                        if 'review_count' in business:
                            review_count = business['review_count']

                        rating =""
                        if 'rating' in business:
                            rating = business['rating']

                        url =""
                        if 'url' in business:
                            url = business['url']
                            url = urllib.parse.urlparse(url)
                            url = urllib.parse.urlunparse((url.scheme, url.netloc, url.path, '', '', ''))


                        queries.append( (business_id, business_name, business_phone, address_line1, address_line2, address_line3, city, postal_code, state_code, is_closed, review_count, rating, store_types, url, None) )
                    c.executemany('INSERT OR IGNORE INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', queries)
                    conn.commit()
            except urllib.error.HTTPError as error:
                if error.code == 400:
                    print('exception 400 on location {}'.format(zip_code))
                else:
                    sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))
            else:
                c.execute('INSERT INTO geography VALUES (?,?,?)', (region['center']['longitude'], region['center']['latitude'], zip_code))
            conn.commit()

            print(zip_code)

    conn.close()


if __name__ == '__main__':
    main()
