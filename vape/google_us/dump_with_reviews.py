#!/usr/bin/env python3
import pickle
import csv
import glob
import os.path

def mapped(value, key):
    new_dict = {}

    if key == 'address_components_':
        return mapped_components(value, key)

    if type(value) == dict:
        iterator = list(value.items())
    if type(value) == list:
        iterator = enumerate(value)

    for local_key, value in iterator:
        new_key = key+str(local_key)
        if type(value) in (str, int, float, bool):
            new_dict[new_key] = value
            continue
        if type(value) == dict:
            new_dict.update(mapped(value, new_key+'_'))
        if type(value) == list:
            new_dict.update(mapped(value, new_key+'_'))

    return(new_dict)

def mapped_components(value, key):
    new_dict = {}

    for component in value:
        ctype = 'undefined'
        if len(component['types']) > 0:
            ctype = component['types'][0]
        else:
            print(component)
        new_key = key+ctype+'_'

        new_dict[new_key+'long_name'] = component['long_name']
        new_dict[new_key+'short_name'] = component['short_name']

    return(new_dict)

terms = dict()
for term_file in glob.glob('terms_results/*'):
    file_name = os.path.basename(term_file)
    terms[file_name] = set()
    with open(term_file) as f:
        for line in f:
            terms[file_name].add(line.strip())
#print(terms)

with open('details.pkl', 'rb') as f:
    details = pickle.load(f)

result_list = []

keys = set()

for result in list(details.values()):
    if 'result' not in result:
        continue
    contents = result['result']
    del contents['reference']

    if 'opening_hours' in contents and 'open_now' in contents['opening_hours']:
        del contents['opening_hours']['open_now']



    skip = False
    for component in contents['address_components']:
        if len(component['types']) and component['types'][0] == 'country':
            if component['short_name'] != 'US':
                skip = True

#    for component in contents['address_components']:
#        if len(component['types']) and component['types'][0] == 'administrative_area_level_1':
#            if component['short_name'] != 'CA':
#                skip = True

    if skip:
        continue

    new_dict = dict()
    new_dict.update(mapped(contents, ''))

    for key,value in list(terms.items()):
        new_dict['returned_for_'+key] = new_dict['place_id'] in value

    result_list.append(new_dict)
    keys.update(set(new_dict.keys()))

print(keys)
print((len(result_list)))

with open('google_with_reviews.csv', 'w') as csv_file:
    writer = csv.DictWriter(csv_file, sorted(keys))
    writer.writeheader()

    for result in result_list:
        writer.writerow(result)
