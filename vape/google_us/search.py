#!/usr/bin/env python3
import argparse
import urllib.request, urllib.error, urllib.parse
import json
import time
import sys
import pickle
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

key='AIzaSyCBFfuzsVbIOzyxYDnrOCq8f4y01lLZW6k'
rankby='distance'

parser = argparse.ArgumentParser()
parser.add_argument('search_term')
args = parser.parse_args()

places = set()

with open('../geocodes.pkl', 'rb') as f:
    zip_codes = pickle.load(f)
    for zip_code, data in sorted(zip_codes.items()):
        time.sleep(1)
        if len(data) == 0:
            print(zip_code, " is zero length")
            continue
        geometry = data[0]['geometry']
        center = geometry['location']
        if 'bounds' in geometry:
            ne = geometry['bounds']['northeast']
            sw = geometry['bounds']['southwest']
            r1 = haversine(center['lng'], center['lat'], ne['lng'], ne['lat'])
            r2 = haversine(center['lng'], center['lat'], sw['lng'], sw['lat'])

            max_r = max(r1, r2)
        else:
            max_r = 172.6337261384751

        print(zip_code)


        location = str(center['lat']) + ',' + str(center['lng'])

        params = urllib.parse.urlencode({
            'keyword': args.search_term,
            'location': location,
            'rankby': rankby,
            'key': key
        })

        while True:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?%s" % params

            #print(url)

            for i in range(10):
                try:
                    response=urllib.request.urlopen(url).read().decode('utf-8')
                except urllib.error.URLError:
                    time.sleep(10)
                    print('retrying ',zip_code)
                    continue
                else:
                    break
            else:
                sys.exit(1)

            #print(json.dumps(json.loads(response), sort_keys=True,indent=4,separators=(',', ': ')))
            contents = json.loads(response)
            results = contents["results"]

            for result in results:
                places.add(result['place_id'])
                loc = result['geometry']['location']
                radius = haversine(center['lng'], center['lat'], loc['lng'], loc['lat'])
                #print(radius, max_r)

            # exit if there are no more results in the region
            if not (len(results) == 20 and
                    radius < max_r and
                    'next_page_token' in contents):
                break

            # update next page token in the params
            params['pagetoken'] = contents["next_page_token"]

            time.sleep(5)
            
with open('terms_results/'+args.search_term, 'w') as f:
    for place in places:
        print(place, file=f)