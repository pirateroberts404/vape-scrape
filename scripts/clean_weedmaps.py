import pandas as pd
import numpy as np
import re

def remove_symbol(row, col, left, right):
    if pd.isnull(row[col]):
        return ""
    return re.sub(left, right, row[col], flags = re.I)

def main():
	weedmaps = pd.read_csv("..//data//store.csv")
	weedmaps.phone = weedmaps.apply(lambda row: remove_symbol(row, "phone", "\(|\)|-|\s|\.|\+", ""), axis = 1).astype(str)
	weedmaps.zip_code = weedmaps.zip_code.astype(str)
	weedmaps.city = weedmaps.city.str.lower()
	weedmaps = weedmaps.fillna("")
	weedmaps.to_csv("..//data//store_clean.csv", index = False)