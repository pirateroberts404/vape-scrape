import pandas as pd
import numpy as np
import re
import nltk
import json

def fix_nums(s):
    if pd.isnull(s):
        return np.nan
    else:
        return s.replace(".0", "")

def search_column(row, col, string):
    if pd.isnull(row[col]):
        return False
    elif re.search(string, row[col], flags = re.I) != None:
        return True
    else:
        return False

def update_matches(test, matches, num):
    
    for match in test.id:
        if match not in matches:
            matches.update({match: num})
        else:
            matches[match] += num
    
    return matches


def suggest_stores(master_list, left_to_join, weedmaps):
    
    tmp = 0
    ranked_indexes = {}
    unique_cities = weedmaps.city.unique()
    unique_phones = weedmaps.phone.unique()
    unique_website = [x.strip() for x in weedmaps.website.unique() if not pd.isnull(x)]
    unique_emails = [x.strip() for x in weedmaps.email.unique() if not pd.isnull(x)]
    
    for unjoined_store in left_to_join:
        
        comparison = master_list[master_list["License_no_dash"] == unjoined_store]
        matches = {}
        
        # compare website
        if not pd.isnull(comparison.website.iloc[0]):
            best_site = sorted({x: nltk.edit_distance(comparison.website.iloc[0], str(x)) for x in unique_website}.items(), key = lambda x: x[1])[0]
            if best_site[1] <= 2:
                test = weedmaps[weedmaps.apply(lambda row: search_column(row, "website", best_site[0]), axis = 1)]
                matches = update_matches(test, matches, 2)
        
        
        # compare email
        if not pd.isnull(comparison.email.iloc[0]):
            best_email = sorted({x: nltk.edit_distance(comparison.email.iloc[0], str(x)) for x in unique_emails}.items(), key = lambda x: x[1])[0]
            if best_email[1] <= 2:
                test = weedmaps[weedmaps.apply(lambda row: search_column(row, "email", best_email[0]), axis = 1)]
                matches = update_matches(test, matches, 2)
        
        
        # compare phone
        if not pd.isnull(comparison.phone.iloc[0]):
            best_phone = sorted({x: nltk.edit_distance(comparison.phone.iloc[0], x) for x in unique_phones}.items(), key = lambda x: x[1])[0]
            if best_phone[1] <= 1:
                test = weedmaps[weedmaps.apply(lambda row: search_column(row, "phone", best_phone[0]), axis = 1)]
                matches = update_matches(test, matches, 2)
        
        
        # compare city
        if not pd.isnull(comparison.city.iloc[0]):
            best_city = sorted({x: nltk.edit_distance(comparison.city.iloc[0], x) for x in unique_cities}.items(), key = lambda x: x[1])[0][0]
            test = weedmaps[weedmaps.apply(lambda row: search_column(row, "city", best_city), axis = 1)]    
            matches = update_matches(test, matches, 1)
            
            
        # compare names
        if not pd.isnull(comparison.company_name.iloc[0]):
            best_name = sorted({x: nltk.edit_distance(comparison.company_name.iloc[0], x) for x in unique_cities}.items(), key = lambda x: x[1])[0][0]
            test = weedmaps[weedmaps.apply(lambda row: search_column(row, "name", best_city), axis = 1)]
            matches = update_matches(test, matches, 1)  
        
        
        # compare zip
        test = weedmaps[weedmaps.apply(lambda row: search_column(row, "zip_code", comparison.zip_code.iloc[0]), axis = 1)]
        matches = update_matches(test, matches, 1)
        
        ranked_indexes.update({unjoined_store: sorted(matches.items(), key = lambda x: x[1], reverse = True)})
        
    return ranked_indexes

def main(name):
    left_to_join = json.load(open("..//data//latent.json", "r"))
    left_to_join = [x[0] for x in list(filter(lambda x: x[1] == 0, {x: len(left_to_join[x]) for x in left_to_join}.items()))]
    master_list = pd.read_csv("..//data//{}_active_retailers.csv".format(name), low_memory = False)
    master_list.zip_code = master_list.zip_code.fillna("").astype(str).apply(lambda x: fix_nums(x))
    master_list.phone = master_list.phone.fillna("").astype(str).apply(lambda x: fix_nums(x))
    weedmaps = pd.read_csv("..//data//weedmaps_not_joined.csv")
    all_matches = suggest_stores(master_list, left_to_join, weedmaps)

    with open("..//data//matches.json", "w") as f:
        json.dump(all_matches, f)

if __name__ == '__main__':
    main()