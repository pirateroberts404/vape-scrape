import pandas as pd
import numpy as np
import json
import pickle


def add_match_license(license_number, list_wm_id):
    global licenses_joined
    global licenses_not_joined
    global stores_not_joined
    global stores
    global licenses
    
    if -1 in list_wm_id:
        list_wm_id.remove(-1)
    
    if len(list_wm_id) < 1:
        licenses_not_joined = licenses_not_joined[licenses_not_joined['License_no_dash'] != license_number]
    for wm_id in list_wm_id:
        stores_not_joined = stores_not_joined[stores_not_joined['id'] != int(wm_id)]
        store_found = stores[stores['id'] == int(wm_id)].copy()
        store_found['License_no_dash'] = license_number
        license_found = licenses[licenses['License_no_dash'] == license_number]
        match_found = pd.merge(store_found, license_found, left_on = 'License_no_dash', right_on = 'License_no_dash', how = 'inner')
        licenses_joined = licenses_joined.append(match_found, ignore_index = True, sort = False)

def create_matches_csv(_latent_json):
    global licenses_joined
    global licenses_not_joined
    global stores_not_joined
    global stores
    global licenses
    automatic_joined = pd.read_csv("..//data/licenses_joined.csv")
    stores = pd.read_csv("..//data/store.csv")
    licenses = pd.read_csv("..//data/searchResults_clean.csv")
    licenses_joined = pd.DataFrame(columns = automatic_joined.columns)
    licenses_not_joined = pd.read_csv("..//data/searchResults_clean.csv")
    stores_not_joined = pd.read_csv("..//data//store.csv")
    for k, v in _latent_json.items():
        add_match_license(k,v)

def create_cvs_files():
    licenses_joined.to_csv("final_licenses_joined.csv", index = False)
    licenses_not_joined.to_csv("final_licenses_not_joined.csv", index = False)
    stores_not_joined.to_csv("final_stores_not_joined.csv", index = False)

def main():
      with open("..//data//latent.json", "r") as f:
            latent_json = json.load(f)

      create_matches_csv(latent_json)
      create_cvs_files()


if __name__ == '__main__':
      main()


