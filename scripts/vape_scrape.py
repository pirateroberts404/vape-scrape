import pandas as pd
import sys

import clean_master_data
import create_database
import scrape_weedmaps
import output_csv
import join_master_and_weedmaps

def main():
    print(sys.argv)
    name = input("What is the name of the masterfile? Include the file extension (for example, searchResults.csv).\n").strip()
    try:
        master_list = pd.read_csv("..//data//{}".format(name))
    except FileNotFoundError as e:
        print(e)
        print("Make sure the masterfile is located in a directory called data.")
        return

    print("Stage 1: Clean master file")
    clean_master_data.main(name)
    print("\nStage 2: Create database")
    create_database.main()
    print("\nStage 3: Scraping Weedmaps")
    scrape_weedmaps.main()

if __name__ == "__main__":
    main()