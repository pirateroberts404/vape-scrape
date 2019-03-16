import pandas as pd
import numpy as np
import re
import nltk
import json

def find_bad_row(row, col, term):
    if re.search(term, row[col], flags = re.I) is not None:
        return True
    return False

def break_fields(row, col, string):
    if pd.isnull(row[col]):
        return ""
    
    test = re.search(string, row[col], flags = re.I)
    if test != None:
        return test.group()
    
    return ""

def get_city(row, col):
    street_abbrev = [" w ", " blvd ", " st ", " rd ", " pkwy ", " ave ", 
                     " ctr ", " cir ", " ct ", " dr ", " ln ", " lk ", 
                     " lp ", " pl ", " sq ", " tr ", " e ", " n ", " s ", 
                     " hwy ", " way ", " wy ", ]
    fix = {"[0-9]": "", "\s+": " ", "san fran": "san francisco", "avenue": "", "highway": ""}
    if pd.isnull(row[col]):
        return ""
    
    left_limit = 0
    check_list = []
    for i in street_abbrev:
        street = re.search(i, row[col], flags = re.I)
        if street != None:  
            check_list.append(street.end())
        else:
            check_list.append(0)
    left_limit = max(check_list)
    
    right_limit = re.search(", ", row[col], flags = re.I)
    if right_limit != None:
        right_limit = right_limit.start()
        
    tmp = row[col][left_limit: right_limit].strip()
    
    for i in fix:
        tmp = re.sub(i, fix[i], tmp, flags = re.I)
        
    return tmp.strip()

def get_city(row, col):
    street_abbrev = [" w ", " blvd ", " st ", " rd ", " pkwy ", " ave ", 
                     " ctr ", " cir ", " ct ", " dr ", " ln ", " lk ", 
                     " lp ", " pl ", " sq ", " tr ", " e ", " n ", " s ", 
                     " hwy ", " way ", " wy ", ]
    fix = {"[0-9]": "", "\s+": " ", "san fran": "san francisco", "avenue": "", "highway": "", "san franciscocisco": "san francisco"}
    if pd.isnull(row[col]):
        return ""
    
    left_limit = 0
    check_list = []
    for i in street_abbrev:
        street = re.search(i, row[col], flags = re.I)
        if street != None:  
            check_list.append(street.end())
        else:
            check_list.append(0)
    left_limit = max(check_list)
    
    right_limit = re.search(", ", row[col], flags = re.I)
    if right_limit != None:
        right_limit = right_limit.start()
        
    tmp = row[col][left_limit: right_limit].strip()
    
    for i in fix:
        tmp = re.sub(i, fix[i], tmp, flags = re.I)
        
    return tmp.strip()

def get_email(row, col):
    replace = {"email": "", "Email": "", "-": ""}
    if pd.isnull(row[col]):
        return ""
    check = re.search("email.{,1}?-.+?@.+?\s", row[col], flags = re.I)
    
    if check is not None:
        check = check.group()
        for i in replace:
            check = check.replace(i, replace[i])
        return check.strip()
    
    return ""

def get_website(row, col):
    if pd.isnull(row[col]):
        return ""
    check = re.search("website-", row[col], flags = re.I)
    
    if check is not None:
        check = row[col][check.end():]
        return check.strip()
    
    return ""

def get_name(row, col):
    if pd.isnull(row[col]):
        return ""
    check = re.search(":", row[col], flags = re.I)
    
    if check is not None:
        check = row[col][:check.end() - 1]
        return check.strip()
    
    return ""

def get_phone(row, col):
    if pd.isnull(row[col]):
        return ""
    
    check = re.search("phone-.+?\s", row[col], flags = re.I)
    
    if check is not None:
        check = re.sub("-|:|\(|\)|phone", "", check.group(), flags = re.I)
        return check.strip()
        
    return ""

def main():
    name = input("What is the name of the masterfile? Include the extension (for example, searchResults.csv).\n").strip()
    try:
        master_list = pd.read_csv("..//data//{}".format(name))
    except FileNotFoundError as e:
        print(e)
        print("Make sure the masterfile is located in a directory called data.")
        return
        
    bad_indexes = master_list.apply(lambda row: find_bad_row(row, "License Number", "license number"), axis = 1)
    master_list = master_list[~bad_indexes].reset_index(drop = True)
    master_list["zip_code"] = master_list.apply(lambda row: break_fields(row, "Premise Address", "([0-9]{5})|([0-9]{9})"), axis = 1)
    master_list["city"] = master_list.apply(lambda row: get_city(row, "Premise Address"), axis = 1).str.lower()
    master_list["email"] = master_list.apply(lambda row: get_email(row, "Business Contact Information"), axis = 1).str.lower()
    master_list["website"] = master_list.apply(lambda row: get_website(row, "Business Contact Information"), axis = 1).str.lower()
    master_list["company_name"] = master_list.apply(lambda row: get_name(row, "Business Contact Information"), axis = 1).str.lower()
    master_list["phone"] = master_list.apply(lambda row: get_phone(row, "Business Contact Information"), axis = 1).astype(str)
    master_list["License_no_dash"] = master_list["License Number"].str.replace("-", "")
    cleaned_name = "../data/{}_clean.csv".format(name.replace(".csv", ""))
    print("Outputting cleaned {} as {}".format(name, cleaned_name)) 
    master_list.to_csv(cleaned_name, index = False)
    retailers = master_list[master_list["License Type"].isin(["Cannabis - Retailer Temporary License", "Cannabis - Retailer Nonstorefront Temporary License"])]
    retailers = retailers[retailers.Status == "Active"]
    active = "../data/{}_active_retailers.csv".format(name.replace(".csv", ""))
    print("Outputting active retailers as {}".format(active))
    retailers.to_csv(active, index = False)
    
if __name__ == "__main__":
    main()