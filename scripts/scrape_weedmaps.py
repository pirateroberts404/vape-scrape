import matplotlib.pyplot as plt
import numpy as np
import time
import requests
import sqlite3
import json
import html2text
import re

from itertools import product
from lxml import html

def sleep_time(base = 1, tolerance = 1):
    
    choose = np.random.uniform(0, 1)
    
    if 0 <= choose <= 0.9:
        return np.random.uniform(base, base + tolerance)
    if 0.9 < choose <= 0.99:
        return np.random.uniform((base + tolerance) * 2, (base + tolerance) * 3)
    else:
        return np.random.uniform((base + tolerance) * 6, (base + tolerance) * 7)
    

def depth(file):
    """
    Finds depth of JSON-formatted file.
    """
    if type(file) == dict:
        for key in file.keys():
            return 1 + max([0] + [depth(file[key])])
    elif type(file) == list:
        for item in file:
            return 1 + max([0] + [depth(item)])
    else:
        return 1
    
def build_bounding_box(coord, lat_width = 1, long_width = 1):
    """
    coord: A valid coordinate for a specific state. Format is (latitude, longitude)
    """
    lowerleft = (coord[0] - (lat_width / 2), coord[1] - (long_width / 2))
    upperright = (coord[0] + (lat_width / 2), coord[1] + (long_width / 2))
    
    return lowerleft, upperright


def parse_storefronts_in_box(coord):
    """
    coord: one box location.
    """
    
    link = "https://api-g.weedmaps.com/discovery/v1/listings?filter%5Bany_retailer_services%5D%5B%5D=storefront&filter%5Bany_retailer_services%5D%5B%5D=delivery&filter%5Bbounding_box%5D={},{},{},{}&page_size=100&size=2000"
    lowerleft, upperright = build_bounding_box(coord)
    link = link.format(lowerleft[0], lowerleft[1], upperright[0], upperright[1])
    response = requests.get(link).json()["data"]["listings"]
    queries = []
    
    # if there are actually results
    if len(response) > 0:
        
        conn = sqlite3.connect("..//data//weedmaps.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        for result in response:
            
            identity = ""
            if "id" in result:
                identity = result["id"]
                
            name = ""
            if "name" in result:
                name = result["name"]  
                
            state = ""
            if "state" in result:
                state = result["state"]
                
            city = ""
            if "city" in result:
                city = result["city"]

            latitude = ""
            if "latitude" in result:
                latitude = float(result["latitude"])
                
            longitude = ""
            if "longitude" in result:
                longitude = float(result["longitude"])
                
            license_type = ""
            if "license_type" in result:
                license_type = result["license_type"]
                
            address = ""
            if "address" in result:
                address = result["address"]
                
            rating = ""
            if "rating" in result:
                rating = int(result["rating"])
                
            reviews_count = ""
            if "reviews_count" in result:
                reviews_count = int(result["reviews_count"])
                
            zip_code = ""
            if "zip_code" in result:
                zip_code = result["zip_code"]
                
            web_url = ""
            if "web_url" in result:
                web_url = result["web_url"]          
                
            retailer_services = ""
            if "retailer_services" in result:
                retailer_services = result["retailer_services"][0]
                
            slug = ""
            if "slug" in result:
                slug = result["slug"]
                

            
            # at this point, go find the strains, phone number, etc. and add to other database
            phone, license, license_names, email, website = get_metadata(identity, slug, retailer_services, c, conn)
            
            if len(phone) == 0:
                phone = ""
            else:
                phone = phone[0]
            
            temp = [identity, name, state, city, latitude, longitude,
                            license_type, address, rating, reviews_count, zip_code, 
                            web_url, retailer_services, phone, email, website]

            for checker in license_types:
                if checker in license_names:
                    i = license_names.index(checker)
                    temp.append(license[i])
                else:
                    temp.append("")
            
            queries.append(temp)
        
        c.executemany("INSERT OR IGNORE INTO store VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", queries)
        conn.commit()
        conn.close()
        
def get_metadata(identity, slug, retailer_services, c, conn):
    
    """
    This function gets metadata that is not available in the API call.
    It also build the strain database.
    
    identity: ID of the dispensary
    slug: name of dispensary in API
    retailer_services: whether it is a dispensary or a doctor
    c: cursor for database
    """
    
    # build search url
    dis = "https://weedmaps.com/"
    base_link = "https://api-g.weedmaps.com/discovery/v1/listings/"
    if retailer_services == "storefront":
        base_link += "dispensaries/"
        dis += "dispensaries/"
    elif retailer_services == "delivery":
        base_link += "deliveries/"
        dis += "deliveries/"
    base_link += slug + "/"
    menu_items = "menu_items?page={}&page_size=150&limit=150"
    strain_queries = []
                
    check = requests.get(dis + slug)
    tree = html.fromstring(check.content)
    
    # get license, telephone, email, and website
    # get license
    try:
        license = tree.xpath('//*[@id="collapsible-container"]/div[1]/div[1]/ul/li/text()[3]')
        license_name = tree.xpath('//*[@id="collapsible-container"]/div[1]/div[1]/ul/li/text()[1]')
    except:
        license = []
        license_name = []
    
    # telephone
    try:
        telephone = tree.xpath('//*[@id="collapsible-container"]/div[1]/div[1]/div[1]/ul/li[1]/a/text()')
    except:
        telephone = ""
        
    # email
    try:
        email = tree.xpath('//*[@id="collapsible-container"]/div[1]/div[1]/div[1]/ul/li[2]/a/text()')  
    except:
        email = ""
        
    # website
    try:
        website = tree.xpath('//*[@id="collapsible-container"]/div[1]/div[1]/div[1]/ul/li[3]/a/text()')
    except:
        website = ""
        
    #print(license, license_name, telephone, email, website)

    # now that we have ID's, we can now check the menu.
    all_items = requests.get(base_link + menu_items.format(1)).json()
    if "data" in all_items:
        
        num_pages = int(np.ceil(all_items["meta"]["total_menu_items"] / 150))
        
        for page in range(1, num_pages + 1):
            
            total_items = 0
            
            # save some time on page one, reuse the last query
            if page == 1:
                
                for item in all_items["data"]["menu_items"]:

                    # get name of strain
                    name = ""
                    if item["name"] != None:
                        name = item["name"]
                    
                    # get type of strain
                    strain = ""
                    if item["category"]["name"] != None:
                        strain = item["category"]["name"]
                        if strain not in ["Hybrid", "Indica", "Sativa"]:
                            continue
                        total_items += 1
                        
                    # get prices
                    strain_queries = get_prices(strain_queries, item, identity, name, strain)
                    
            #on second page of menu
            else:
                all_items = requests.get(base_link + menu_items.format(page)).json()
                
                for item in all_items["data"]["menu_items"]:
                    
                    # get name of strain
                    name = ""
                    if item["name"] != None:
                        name = item["name"]
                    
                    # get type of strain
                    strain = ""
                    if item["category"]["name"] != None:
                        strain = item["category"]["name"]
                        if strain not in ["Hybrid", "Indica", "Sativa"]:
                            continue
                        total_items += 1
                        
                    # get all prices for each item
                    strain_queries = get_prices(strain_queries, item, identity, name, strain)
        
        c.executemany("INSERT OR IGNORE INTO strain VALUES (?,?,?,?,?,?,?)", strain_queries)
        conn.commit()
    return telephone, license, license_name, email, website
        
def find_stores(lattice, base, tolerance):
    """
    Takes a lattice, finds all stores, and adds to database.
    """
    
    license_types = json.load(open("..//data//license_types.json", "rb"))
    
    for point in lattice:
        parse_storefronts_in_box(point, license_types)
        time.sleep(sleep_time(base, tolerance))
        
        
def get_prices(strain_queries, item, identity, name, strain):
    
    if item["prices"] != None:
        
        grams_per_eighth = np.float("inf")
        if "grams_per_eighth" in item["prices"]:
            grams_per_eighth = item["prices"]["grams_per_eighth"]

        # only have grams per eighth
        if len(item["prices"]) == 1:
            strain_queries.append((identity, name, "", "", "", "", grams_per_eighth))

        # looks like this: {'price': 6.0, 'units': '1'} or similar
        elif depth(item["prices"]) == 2:
                for attr in item["prices"]:
                    if attr == "price":
                        price = item["prices"][attr]
                    elif attr == "units":
                        amount = item["prices"][attr]
                        strain_queries.append((identity, name, strain, price, amount, "", grams_per_eighth))

        # looks normal
        else:
            for unit in item["prices"]:
                if unit == "grams_per_eighth":
                    grams_per_eighth = item["prices"]["grams_per_eighth"]
                else:

                    # if there is only one price
                    if type(item["prices"][unit]) == dict:
                        for attr in item["prices"][unit]:
                            if attr == "price":
                                price = item["prices"][unit][attr]
                            elif attr == "units":
                                amount = item["prices"][unit][attr]
                                strain_queries.append((identity, name, strain, price, amount, unit, grams_per_eighth))

                    # if there are multiple pricings
                    elif type(item["prices"][unit]) == list:
                        for pricing in item["prices"][unit]:
                            for attr in pricing:
                                if attr == "price":
                                    price = pricing[attr]
                                elif attr == "units":
                                    amount = pricing[attr]
                                    strain_queries.append((identity, name, strain, price, amount, unit, grams_per_eighth))
    return strain_queries


def main():
    california_lattice = json.load(open("..//data//california_lattice.json", "rb"))
    print("Beginning to scrape Weedmaps in California...")
    print()
    find_stores(california_lattice, 0, 1)
    print("Finished scraping Weedmaps")
    
    
if __name__ == '__main__':
    main()