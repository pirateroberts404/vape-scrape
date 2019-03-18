import pandas as pd
import sys
import glob

import clean_master_data
import create_database
import delete_database
import scrape_weedmaps
import output_csv
import clean_weedmaps
import join_master_and_weedmaps
import create_matches

def main():
    
    #name = input("What is the name of the masterfile? Include the file extension (for example, searchResults.csv).\n").strip()
    #try:
    #    master_list = pd.read_csv("..//data//{}".format(name))
    #except FileNotFoundError as e:
    #    print(e)
    #    print("Make sure the masterfile is located in a directory called data.")
    #    return

    options = sys.argv
    c = 5
    if "--help" in options:
        print("""
Usage: weedmaps_scrape.py [options] -name <name_of_masterfile>

Pipeline options:
--create                    Creates a new SQL database for data scraped from Weedmaps
--skip-scrape               Skips scraping data from Weedmaps
--API-limit-pause   <int>   Sets number of seconds to retry an API call to Weedmaps if Weedmaps returns an "API limit exceeded" message
            """)
        return

    if "-name" not in options:
        print("Please specify a name for the master file.")
        return
    else:
        name = options[options.index("-name") + 1]
        nocsv = name.replace(".csv", "")

    if "--API-limit-pause" in options:
        c = int(options[options.index("--API-limit-pause") + 1])
    # Stage 1
    if "--create" in options:
        print("Deleting existing Weedmaps database\n")
        datafiles = glob.glob("..\\data\\*")

        # checking if weedmaps.db already exists
        if sum([True for x in datafiles if "weedmaps.db" in x]):
            delete_database.main()
        else:
            print("No existing Weedmaps database found. Moving on.")

        print("\nStage 1: Create database")
        create_database.main()
    else:
        print("Skipping Stage 1: Create database")

    # Stage 2
    print("\nStage 2: Clean master file")
    clean_master_data.main(name)

    # Stage 3
    if "--skip-scrape" in options:
        print("\nSkipping Stage 3: Scraping Weedmaps")
    else:
        print("\nStage 3: Scraping Weedmaps")
        scrape_weedmaps.main(c)

    # Stage 4
    print("\nStage 4: Creating .csv files from SQL database")
    output_csv.main()

    # Stage 5
    print("\nStage 5: Clean Weedmaps store file")
    clean_weedmaps.main()

    # Stage 6
    print("\nStage 6: Joining master file and weedmaps scrape")
    join_master_and_weedmaps.main(nocsv)

    # Stage 7
    print("\nStage 7: Suggesting Weedmaps stores for unjoined stores in master file")
    create_matches.main(nocsv)

    print("\nFinished. You may now use the interface to manually join stores.")


if __name__ == "__main__":
    main()