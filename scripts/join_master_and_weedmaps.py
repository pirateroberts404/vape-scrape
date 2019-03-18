import pandas as pd
import numpy as np
import glob
import re
import json

def main(name):

    licenses = pd.read_csv("..//data//{}_active_retailers.csv".format(name))
    weedmaps_not_joined = pd.read_csv("..//data//store_clean.csv")
    check_cols = ["adult_use_cultivation", "adult_use_nonstorefront", 
                  "adult_use_retail", "distributor", "medical_cultivation", 
                  "medical_nonstorefront", "medical_retail", "microbusiness"]

    licenses['License Number'] = licenses['License Number'].str.replace('-', '')

    for col in check_cols:
        if weedmaps_not_joined[col].dtype != "float":
            weedmaps_not_joined[col] = weedmaps_not_joined[col].str.upper()
            weedmaps_not_joined[col] = weedmaps_not_joined[col].str.replace('-', '')

    licenses_joined = pd.DataFrame()
    licenses_not_joined = licenses.copy()
    #c = 0
    for i in check_cols:
        try:
            join_on_i = pd.merge(weedmaps_not_joined, licenses, left_on = i, right_on = 'License Number', how = 'inner')

            licenses_not_joined = licenses_not_joined[~licenses_not_joined["License Number"].isin(join_on_i["License Number"])]
            licenses_joined = pd.concat([licenses_joined, join_on_i])
            weedmaps_not_joined = weedmaps_not_joined[~weedmaps_not_joined[i].isin(join_on_i[i])]
             
        except:
            pass

    latent_data_structure = {}
    for license in licenses_joined["License Number"].unique():
        latent_data_structure.update({license: licenses_joined[licenses_joined["License Number"] == license].id.tolist()})
        
    for license in licenses_not_joined["License Number"].unique():
        #if licenses_not_joined[licenses_not_joined["License Number"] == license]["License Type"].iloc[0] in ['Cannabis - Retailer Temporary License', 'Cannabis - Retailer Nonstorefront Temporary License']:
        latent_data_structure.update({license: []})

    with open("..//data//latent.json", "w") as f:
        json.dump(latent_data_structure, f)

    print("\n{} out of {} master file licenses joined.".format(len(licenses_joined["License Number"].unique()), len(licenses["License Number"].unique())))

    licenses_not_joined.phone = licenses_not_joined.phone.astype(np.int64, errors = "ignore")
    licenses_not_joined.to_csv("..//data//licenses_not_joined.csv", index = False)
    licenses_joined.to_csv('..//data//licenses_joined.csv', index = False)
    weedmaps_not_joined.to_csv("..//data//weedmaps_not_joined.csv", index = False)

if __name__ == "__main__":
    main()

