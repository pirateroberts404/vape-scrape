Steps to run:

Search on google for 'vaporizer store'
$ ./search.py 'vaporizer store'

This creates a text file 'vaporizer store' in the terms_results directory

Next, we ask the Google api for details about each store.
$ ./details.py

Categories have to be obtained outside the official Google api
$ ./add_categories.py

Now, we can dump the results
$ ./dump_with_reviews.py
