import sqlite3
def main():
    conn = sqlite3.connect('test_us.db')
    c = conn.cursor()

    c.execute("CREATE TABLE entries (yelp_id TEXT UNIQUE, name TEXT, phone TEXT, address_line1 TEXT, address_line2 TEXT, address_line3 TEXT, city TEXT, postal_code TEXT, state_code TEXT, is_closed INT, review_count INT, rating REAL, store_types TEXT, url TEXT, true_url TEXT);")
    c.execute("CREATE TABLE search_names (yelp_id TEXT UNIQUE);")
    c.execute("CREATE TABLE geography (center_long REAL, center_lat REAL, zip_code INT);")
    c.execute("CREATE TABLE search_entries (yelp_id TEXT UNIQUE, name TEXT, phone TEXT, address_line1 TEXT, address_line2 TEXT, address_line3 TEXT, city TEXT, postal_code TEXT, state_code TEXT, is_closed INT, review_count INT, rating REAL, store_types TEXT, true_url TEXT);")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
