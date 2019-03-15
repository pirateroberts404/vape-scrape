import numpy as np
import time
import requests
import sqlite3
import json
import re
import datetime
import logging
import sys
import gc

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


def get_all_stores(coord, all_stores, lat_width = 1, long_width = 1, scale = 2, initial_try = True):
    
    # base w and height = 1 
    link = "https://api-g.weedmaps.com/discovery/v1/listings?filter%5Bany_retailer_services%5D%5B%5D=storefront&filter%5Bany_retailer_services%5D%5B%5D=delivery&filter%5Bbounding_box%5D={},{},{},{}&page_size=100&size=100"
    lowerleft, upperright = build_bounding_box(coord, lat_width, long_width)
    link = link.format(lowerleft[0], lowerleft[1], upperright[0], upperright[1])
    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename="..//debug//scrape_diagnostics.txt", level=logging.INFO)    
    
    # try to access the API for stores within a bounding box
    cnt = 0
    response = ""
    while response == "":
        try:
            if cnt > 3:
                logger.error("Retried obtaining stores %s times, giving up", str(cnt))
                break
            response = requests.get(link).json()
            # Exceeded API limit
            if "message" in response:
                logger.error("Rate limit exceeded for bounding box %s with latitude width %s and longitude width %s", str(coord), str(lat_width), str(long_width))
                logger.error("Waiting 60 seconds")
                sleep_time(base = 60, tolerance = 0)
                response = ""
        
        # Connection was forcibly shut down
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            logger.error("Connection was forcibly shut down bounding box %s with latitude width %s and longitude width %s", str(coord), str(lat_width), str(long_width))
            logger.error("Waiting 60 seconds")
            sleep_time(base = 60, tolerance = 0)
            cnt += 1
        except Exception as e:
            logger.error(e)
            logger.error("Waiting 60 seconds")
            sleep_time(base = 60, tolerance = 0)
            cnt += 1
            
    # sometimes there is an empty response
    if "data" not in response:
        return
    else:
        listings = response["data"]["listings"]
        total_listings = response["meta"]["total_listings"]

        if initial_try:
            logger = logging.getLogger(__name__)
            logging.basicConfig(filename="..//debug//scrape_diagnostics.txt", level=logging.INFO)
            logger.info("%s stores found in %s", str(total_listings), str(coord))
            #print(total_listings, "stores found in", coord)

        if total_listings < 100:
            if len(listings) > 0:
                for store in listings:
                    all_stores.update({store["id"]: store})
        else:
            
            # subdivide and get midpoints
            upperleft_mid = ((coord[0] + upperright[0]) / scale, (coord[1] + lowerleft[1]) / scale)
            upperright_mid = ((coord[0] + upperright[0]) / scale, (coord[1] + upperright[1]) / scale)
            lowerleft_mid = ((coord[0] + lowerleft[0]) / scale, (coord[1] + lowerleft[1]) / scale)
            lowerright_mid = ((coord[0] + lowerleft[0]) / scale, (coord[1] + upperright[1]) / scale)
            get_all_stores(upperleft_mid, all_stores, lat_width=lat_width / scale, long_width=long_width / scale, initial_try = False)
            get_all_stores(upperright_mid, all_stores, lat_width=lat_width / scale, long_width=long_width / scale, initial_try = False)
            get_all_stores(lowerleft_mid, all_stores, lat_width=lat_width / scale, long_width=long_width / scale, initial_try = False)
            get_all_stores(lowerright_mid, all_stores, lat_width=lat_width / scale, long_width=long_width / scale, initial_try = False)

def parse_storefronts_in_box(coord, license_types):
    """
    coord: one box location.
    """

    queries = []
    all_stores = {}
    get_all_stores(coord, all_stores)
    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename="..//debug//scrape_diagnostics.txt", level=logging.INFO)
    logger.info("%s stores scraped at coordinate %s",len(all_stores), str(coord))

    # if there are actually results
    if len(all_stores) > 0:
    
        all_stores = list(all_stores.values())
        
        conn = sqlite3.connect("..//data//weedmaps.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        for result in all_stores:
            
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
                rating = result["rating"]
                
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
                    
            if len(email) == 0:
                email = ""
            else:
                email = email[0]
                    
            if len(website) == 0:
                website = ""
            else:
                website = website[0]
                
            temp = [identity, name, state, city, latitude, longitude,
                        license_type, address, rating, reviews_count, zip_code, 
                        web_url, retailer_services, phone, email, website]

            for checker in license_types:
                if checker in license_names:
                    i = license_names.index(checker)
                    temp.append(license[i])
                else:
                    temp.append("")

            # add date scraped
            now = datetime.datetime.now().strftime("%Y-%m")
            temp.append(now)
            queries.append(temp)
                
            #except Exception as error:
            #logger.error("failed to get metadata for %s", str(id))

        c.executemany("INSERT or IGNORE INTO store VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", queries)
        conn.commit()
        conn.close()
        
        
def access_attempt(base_link, slug, logger):
    """
    Assumes that there will not always be a well defined store page. This means we cannot keep retrying if the page is actually invalid.
    """

    check = ""
    cnt = 0
    while check == "":  
    
        # requests returned a page but was a failed response
        try:
            if cnt > 2:
                logger.error("Re-tried accessing the store page %s times, giving up", str(cnt))
                break
            check = requests.get(base_link)
            if check.status_code != 200:
                logger.error("Response code %s", str(check.status_code))
                logger.error("API call for %s metadata failed", slug)
                logger.error("Waiting 60 seconds")
                sleep_time(base = 60, tolerance = 0)
                check = ""
                cnt += 1
            
        # connection was forcibly shut down
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
            logger.error("Connection was forcibly shut down for %s when looking at page one menu", slug)
            logger.debug("Waiting 60 seconds")
            sleep_time(base = 60, tolerance = 0)
            cnt += 1
        
        # store page resulted in memoryError
        except MemoryError:
            logger.error("Parsing the store page for %s resulted in a MemoryError", slug)
            break
            
        except KeyboardInterrupt:
            break
            
        except Exception as e:
            logger.error(e)
            logger.debug("Waiting 60 seconds")
            sleep_time(base = 60, tolerance = 0)
            cnt += 1
            
    return check
    
def menu_access_attempt(base_link, menu_items, slug, page):
    """
    Assumes that the menu API call will always return some type of JSON, not an empty string. THis means we can keep retrying until we succeed.
    """

    all_items = ""
    while all_items == "":
        try:
        
            all_items = requests.get(base_link + menu_items.format(page)).json()
            
            # returned a good call but with a API limit exceeded message
            if "message" in all_items:
                logger.error(all_items["message"])
                logger.error("Rate limit exceeded for %s when looking at page one menu", slug)
                logger.error("Waiting 30 seconds")
                sleep_time(base = 60, tolerance = 0)
                all_items = ""
                
        # connection was forcibly shut down
        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            logger.error(e)
            logger.error("Connection was forcibly shut down for %s when looking at page one menu", slug)
            logger.error("Waiting 30 seconds")
            sleep_time(base = 60, tolerance = 0)
            
        # json file was "too large"
        except MemoryError:
            logger.error("Parsing the menu for %s resulted in a MemoryError", slug)
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(e)
            logger.debug("Waiting 60 seconds")
            sleep_time(base = 60, tolerance = 0)
            
    return all_items
        
def get_metadata(identity, slug, retailer_services, c, conn):
    
    """
    This function gets metadata that is not available in the API call.
    It also builds the strain database.
    
    identity: ID of the dispensary
    slug: name of dispensary in API
    retailer_services: whether it is a dispensary or a doctor
    c: cursor for database
    """

    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename="..//debug//scrape_diagnostics.txt", filemode = "w", level=logging.INFO)
    #logger.setLevel(logging.INFO)
    
    # build search url
    dis = "https://weedmaps.com/"
    base_link = "https://api-g.weedmaps.com/discovery/v1/listings/"
    if retailer_services == "storefront":
        base_link += "dispensaries/"
        #dis += "dispensaries/"
    elif retailer_services == "delivery":
        base_link += "deliveries/"
        #dis += "deliveries/"
    base_link += slug + "/"
    menu_items = "menu_items?page={}&page_size=150&limit=150"
    strain_queries = []

    # try setting up the html document into searchable Xpaths
    parsed = False
    cnt = 0
    while not parsed:
        try:
            if cnt > 3:
                logger.error("Re-tried converting HTML %s times, giving up", str(cnt))
                break
            # attempt to access the weedmaps store page for license info
            check = access_attempt(base_link, slug, logger)
            tree = html.fromstring(check.content)
            parsed = True
        except Exception as error:
            logger.error(error)
            logger.error("Failed to convert HTML to tree for %s", slug)
            #logger.error("Raw scraped file", check.content)
            logger.error("Waiting 120 seconds")
            sleep_time(base = 120, tolerance = 0)
            cnt += 1
    
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

    # now that we have the previous fields, we can now check the menu.
    
    # attempt to access the menu with the API
 
    all_items = menu_access_attempt(base_link, menu_items, slug, 1)
    
    # first page of the menu
    if "data" in all_items:
        
        now = datetime.datetime.now().strftime("%Y-%m")
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
                    strain_queries = get_prices(strain_queries, item, identity, name, strain, now)
                    
            #on second page of menu
            else:
                all_items = menu_access_attempt(base_link, menu_items, slug, page)
                
                if "data" in all_items:
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
                        strain_queries = get_prices(strain_queries, item, identity, name, strain, now)
        
        c.executemany("INSERT OR IGNORE INTO strain VALUES (?,?,?,?,?,?,?,?)", strain_queries)
        conn.commit()
    return telephone, license, license_name, email, website

def get_prices(strain_queries, item, identity, name, strain, now):
    
    if item["prices"] != None:
        
        grams_per_eighth = np.float("inf")
        if "grams_per_eighth" in item["prices"]:
            grams_per_eighth = item["prices"]["grams_per_eighth"]

        # only have grams per eighth
        if len(item["prices"]) == 1:
            strain_queries.append((identity, name, "", "", "", "", grams_per_eighth, now))

        # looks like this: {'price': 6.0, 'units': '1'} or similar
        elif depth(item["prices"]) == 2:
                for attr in item["prices"]:
                    if attr == "price":
                        price = item["prices"][attr]
                    elif attr == "units":
                        amount = item["prices"][attr]
                        strain_queries.append((identity, name, strain, price, amount, "", grams_per_eighth, now))

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
                                strain_queries.append((identity, name, strain, price, amount, unit, grams_per_eighth, now))

                    # if there are multiple pricings
                    elif type(item["prices"][unit]) == list:
                        for pricing in item["prices"][unit]:
                            for attr in pricing:
                                if attr == "price":
                                    price = pricing[attr]
                                elif attr == "units":
                                    amount = pricing[attr]
                                    strain_queries.append((identity, name, strain, price, amount, unit, grams_per_eighth, now))
    return strain_queries

    
def find_stores(lattice, base, tolerance):
    """
    Takes a lattice, finds all stores, and adds to database.
    """
    
    license_types = json.load(open("..//data//license_types.json", "rb"))
    
    for point in lattice:
        parse_storefronts_in_box(point, license_types)
        time.sleep(sleep_time(base, tolerance))
        gc.collect()

def main():
    california_lattice = json.load(open("..//data//california_lattice.json", "rb"))
    print("Beginning to scrape Weedmaps in California...")
    c = input("Would you like to traverse the lattice backwards? [Y/N]")
    if c == "Y":
        california_lattice = california_lattice[::-1]
        print("Traversing backwards")
    print()
    find_stores(california_lattice, 1, 1)
    print("Finished scraping Weedmaps in California")
    
    
if __name__ == '__main__':
    """
    possible requests errors:
        - when accessing bounding boxes
        - when accessing the store metadata (in other words, getting the actual page)
        - when accessing the store menu
    """
    logging.basicConfig(filename="..//debug//scrape_diagnostics.txt", filemode = "w", level=logging.DEBUG)
    main()