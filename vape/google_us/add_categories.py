#!/usr/bin/env python3

import pickle
import csv
import glob
import os.path
import urllib.request, urllib.error, urllib.parse
import sys
import time
import zlib
import requests
from hyper.contrib import HTTP20Adapter
from requests.adapters import HTTPAdapter



url_template = 'https://www.google.com/search?tbm=map&fp=1&authuser=0&hl=en&pb=!4m12!1m3!1d9369.106988648073!2d-71.1074225!3d42.34327335!2m3!1f0!2f0!3f0!3m2!1i1229!2i610!4f13.1!7i10!10b1!12m6!2m3!5m1!2b0!20e3!10b1!16b1!19m3!2m2!1i392!2i106!20m40!2m2!1i203!2i100!3m1!2i4!6m6!1m2!1i86!2i86!1m2!1i408!2i256!7m26!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e4!2b0!3e3!1m3!1e3!2b1!3e2!2b1!4b1!9b0!22m6!1s4MLDVrjOOMHte4zRpYgM!4m1!2i11886!7e81!12e5!18e15!24m1!2b1!26m3!2m2!1i80!2i92!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i610!1m6!1m2!1i1179!2i0!2m2!1i1229!2i610!1m6!1m2!1i0!2i0!2m2!1i1229!2i20!1m6!1m2!1i0!2i590!2m2!1i1229!2i610!37m1!1e81!42b1&q={0}&oq={0}&gs_l=maps.3..38.13445.16511.1.17263.19.19.0.0.0.0.2070.3720.9j7j9-1.17.0....0...1ac.1.64.maps..2.15.1635.0.&tch=1&ech=1&psi=4MLDVrjOOMHte4zRpYgM.1455669985653.1'

headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/44.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://www.google.com',
#'Cookie': 'NID=75=Q_cps4uRZ_DTuFRiigvdmSMUNGDF9NrCNGBH1Gnhn_uQQqp_HuyEc3_yqdmcdB_Mhjy5DViinrgf2S-aUXakQ0t_zneEpujeREFp3r94JMNJYC0-cqxiRmW4--DhG7cxRt1vpfCb_WNsFW9Z6gNbSZT9yQicYY0ZuL55KgwLfdyDpgBBudJ7sg; OGPC=5061451-7:',
'Connection': 'keep-alive'
}


with open('details.pkl', 'rb') as f:
    details = pickle.load(f)

result_list = []

keys = set()

for result in list(details.values()):
    if 'result' not in result:
        continue
    contents = result['result']
    if 'store_type' in contents:
        continue
    skip = False
    for component in contents['address_components']:
        if len(component['types']) and component['types'][0] == 'country':
            if component['short_name'] != 'US':
                skip = True
    if skip:
        continue
    store_name = contents['name']
    address = contents['formatted_address']
    print((store_name, address))

    combined = urllib.parse.quote(store_name + ', ' + address)
    url = url_template.format(combined)
    print(url)

    s = requests.Session()
    #s.mount('https://www.google.com', HTTP20Adapter())
    s.mount('https://www.google.com', HTTPAdapter())
    response = s.get(url, headers=headers)
#    print(response.text)
    request = response.text
    index = request.find('Vaporizer Store')
    print(index)
    if index == -1:
        index = request.find('Tobacco Shop')
    if index == -1:
        index = request.find('Store')
    index2 = request.rfind('[', 0, index)
    index3 = request.find(']', index)
    store_types = request[index2+1:index3]

    if 'null' in store_types:
        continue

    store_types = store_types.replace('\\\\u0026', '&')
    store_types = store_types.split(',')
    store_types = [x.strip('\\"') for x in store_types]
    print((store_name, address, store_types))
#    if 'Vaporizer Store' in store_types:
    print((store_name, address, store_types))
    contents['store_type'] = store_types
    with open('details.pkl', 'wb') as f:
        pickle.dump(details, f)

    time.sleep(1.0)

