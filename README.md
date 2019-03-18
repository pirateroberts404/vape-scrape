# Introduction

The [California Bureau of Cannabis Control](https://www.bcc.ca.gov/) is the lead agency in regulating commercial cannabis licenses for medical and adult-use cannabis in California.<sup>1</sup> The BCC provides a list of official cannabis licenses. This repository contains scripts to add additional features for each store, such as cannabis strains offered, geospatial coordinates, and store rating. Data is scraped from Weedmaps, a site where cannabis retailers can list their menus and amenities.

<sup>1</sup> "About Us." *Bureau of Cannabis Control*, 18 March 2019, https://www.bcc.ca.gov/about_us/.

## Requirements

Install the necessary packages with

`pip install -r requirements.txt`

## Command line options

To run the Weedmaps scrape from the command line, type

```
weedmaps_scrape.py [options] -name <name_of_masterfile>
```

### Basic options

`-name <name_of_masterfile>` This is the name of the official list of Cannabis retailer licenses from the California Bureau of Cannabis Control. Required option.

 The official dataset can be downloaded [here](https://aca5.accela.com/bcc/customization/bcc/cap/licenseSearch.aspx). To download, leave all fields blank and click search. Afterwards, click download CSV and wait until a file is downloaded.

`--skip-scrape` Include this flag if you would like to skip scraping Weedmaps.

`--create` Include this flag if you wish to create an entirely new Weedmaps database. 
*Warning:* Including this option deletes all the contents of the database.

`--API-limit-pause <int>`  Sets the number of seconds to retry an API call to Weedmaps if Weedmaps returns an API limit exceeded message. If this flag is excluded, defaults to 5 seconds.




