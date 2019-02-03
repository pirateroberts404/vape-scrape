import sqlite3

def main():

    conn = sqlite3.connect("..//data//weedmaps.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE store (
        id INT UNIQUE, name TEXT, state TEXT, city TEXT, latitude REAL, longitude REAL,
        license_type TEXT, address TEXT, rating REAL, reviews_count INT,
        zip_code TEXT, web_url TEXT, retailer_services TEXT, phone TEXT, 
        adult_use_cultivation TEXT, adult_use_nonstorefront TEXT,
        adult_use_retail TEXT, distributor TEXT, medical_cultivation TEXT,
        medical_nonstorefront TEXT, medical_retail TEXT, microbusiness TEXT
    );
    """)

    c.execute("""
    CREATE TABLE strain (
        id INT, name TEXT, strain TEXT, price REAL, 
        amount TEXT, unit TEXT, grams_per_eighth REAL
    );
    """)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()