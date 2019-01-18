#!/usr/bin/env python3
import urllib.request, urllib.error, urllib.parse
import json
import pickle
import time
import glob
import sys

key='AIzaSyCBFfuzsVbIOzyxYDnrOCq8f4y01lLZW6k'

details = {}

places = set()

for result in glob.glob('terms_results/*'):
    with open(result) as f:
        for line in f:
            places.add(line.strip())

print((len(places)))

for placeid in places:
    params = urllib.parse.urlencode({
        'placeid': placeid,
        'key': key})

    url = "https://maps.googleapis.com/maps/api/place/details/json?%s" % params

    for i in range(10):
        try:
            response=urllib.request.urlopen(url).read().decode('utf-8')
        except urllib.error.URLError:
            time.sleep(10)
            print(('retrying ',placeid))
            continue
        else:
            break
    else:
        sys.exit(1)

    details[placeid] = json.loads(response)
    time.sleep(1.0)

with open('details.pkl', 'wb') as f:
    pickle.dump(details, f)
