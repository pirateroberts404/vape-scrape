import pandas as pd
import glob
import sqlite3

def main():

    conn = sqlite3.connect("..//data//weedmaps.db")
    store_table = pd.read_sql('select * from store', conn)
    strain_table = pd.read_sql("select * from strain", conn)

    store_table.to_csv('..//data//store.csv', index = False)
    strain_table.to_csv('..//data//strain.csv', index = False)
    
if __name__ == '__main__':
    main()