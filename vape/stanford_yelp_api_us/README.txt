Steps to run:

To install the dependencies, run:
$ pip install -r requirements.txt

Create the sqlite database:
$ python create_db.py

This program creates a sqlite database called test_us.db that will store the results
as we go through the other scripts


Get results using the Yelp API:
$ python extract_category_zip_list.py zipcodes_US.txt

This program uses the yelp api to get results in the Vape Shops category, sorted
by distance.

This script prints each zip code it finishes. If the script stops, you can create
a new file, deleting up to the last zip code, and use that as the argument.


Get results using the Yelp search:
$ python search_zipcodes.py zipcodes_US.txt

This program uses yelp search results to get names of Vape Shops in each zip code.

Similarly to extract_category_zip_list.py, this script prints each zip code it
finishes. If the script stops, you can create a new file, deleting up to the last 
zip code, and use that as the argument.


Get true urls for Yelp API results
$ python extract_urls.py

This goes through all Yelp API results and fetches their Yelp page to extract the
web site for the store.


Get all information for search results
$ python remove_search_keys.py
$ python extract_search_urls.py

This goes through all search results that were not returned by the Yelp API. For
each result, it extracts all the information on the result's Yelp page corresponding
to what would have been returned by the Yelp API.


Output CSV
$ python output_csv.py

Outputs a csv file (us.csv) with all the results from the test_us.db database
