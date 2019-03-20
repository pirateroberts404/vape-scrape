import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import pickle
from tempfile import TemporaryFile
import json
import time
import re 


class WeedMapStores:
   def __init__(self, wm_location):
      self.wm_location = wm_location
      self.wm_df = pd.read_csv(wm_location, dtype = {'zip_code': 'str',  'phone' : 'str'})
      self.wm_df = self.wm_df.rename(index = str, columns = {'id': 'id', 'name': 'Name', 'address': 'Address', 'city': 'City', 
                                                         'zip_code': 'Zip Code', 'phone' : 'Phone Number', 'license_type' : 'Adult-Use/Medicinal',
                                                          'web_url': 'WeedMaps URL', 'retailer_services' : 'Services'})
      self.wm_categories = ['id', 'Name', 'Address', 'City', 'Zip Code', 'Phone Number', 'Adult-Use/Medicinal', 'WeedMaps URL', 'Services']

      # Strip strings for cleaner display.
      self.wm_df = self.wm_df[self.wm_categories]
      self.wm_df['Name'] = self.wm_df['Name'].fillna('').str.upper()
      self.wm_df['Address'] = self.wm_df['Address'].fillna('').str.upper()
      self.wm_df['City'] = self.wm_df['City'].fillna('').str.upper()
      self.wm_df['Phone Number'] = self.wm_df['Phone Number'].apply(self.removeSymbols)
      self.wm_df['Adult-Use/Medicinal'] = self.wm_df['Adult-Use/Medicinal'].fillna('').str.upper()
      self.wm_df['WeedMaps URL'] = self.wm_df['WeedMaps URL'].fillna('')


   def removeSymbols(self, phone_number):
      return re.sub('[^0-9]','', phone_number)

   def getSubset(self, wm_id_list):
      try:
         return self.wm_df[self.wm_df['id'].isin(wm_id_list)]
      except:
         print ("Could not find indices {} in weedmaps_df").format(wm_id_list)

   def getWMTuples(self, wm_id_list):
      try:
         wm_subset_df = self.getSubset(wm_id_list)         
         tuples = [tuple(x) for x in wm_subset_df.values]
         return tuples

      except:
         print ("Failed convert tuples. ")



class Licenses:
   def __init__(self, licenses_location):
      self.licenses_location = licenses_location
      self.licenses_df = pd.read_csv(licenses_location, dtype = {'zip_code' : 'str', 'phone' : 'str'})
      self.licenses_df['id'] = "license"
      self.licenses_df = self.licenses_df.rename(index = str, columns = {'company_name' : 'Name', 'Premise Address' : 'Address', 
                                                                        'city' : 'City', 'zip_code' : 'Zip Code', 'phone' : 'Phone Number', 'Adult-Use/Medicinal':  'Adult-Use/Medicinal',
                                                                        'website': 'Web URL', 'License Type': 'License Type', 'Business Owner' : 'Business Owner', 'License Number' : 'License Number'})
      self.licenses_categories = ['id', 'Name', 'Address', 'City', 'Zip Code', 'Phone Number', 'Adult-Use/Medicinal', 'Web URL', 'License Type', 'Business Owner', 'License Number']
      self.licenses_df = self.licenses_df[self.licenses_categories]

      self.licenses_df['Name'] = self.licenses_df['Name'].fillna('').str.upper()
      self.licenses_df['Address'] = self.licenses_df['Address'].fillna('').str.upper()
      self.licenses_df['City'] = self.licenses_df['City'].fillna('').str.upper()
      self.licenses_df['Phone Number'] = self.licenses_df['Phone Number'].fillna('').str.upper()
      self.licenses_df['Adult-Use/Medicinal'] = self.licenses_df['Adult-Use/Medicinal'].fillna('').str.upper()
      self.licenses_df['Web URL'] = self.licenses_df['Web URL'].fillna('').str.upper()
      self.licenses_df['License Type'] = self.licenses_df['License Type'].fillna('').str.upper()
      self.licenses_df['License Number'] = self.licenses_df['License Number'].str.replace("-", "")
      

   def getLicenseTuple(self, license_number):
      try:
         print("license number: " + license_number)
         top_tuple = tuple(self.licenses_df[self.licenses_df['License Number'] == license_number].values[0])
         return top_tuple

      except:
         print ("Could find license number {} ".format(license_number))


class Joining(Licenses, WeedMapStores):
   def __init__(self, licenses_location, wm_location, joined_json_location):
      Licenses.__init__(self, licenses_location)
      WeedMapStores.__init__(self, wm_location)
      self.joined_json_location = joined_json_location
      self.joined_dict = self.get_joined_dictionary(self.joined_json_location)
      self.top_ids = self.get_top_ids()


   def get_joined_dictionary(self, joined_json_location):
      with open (joined_json_location) as joined_file:
         joined_data = json.load(joined_file)

      return joined_data

   def traverse_list(self, current_license_number, forward = True):
      current_license_idx = self.top_ids.index(current_license_number)
   
      if forward:
         if current_license_idx >= len(self.top_ids) - 1:
            return -1
         if len(self.joined_dict[current_license_number]) < 1:
            self.add_join(current_license_number, -1)
         return self.top_ids[current_license_idx + 1]


      if -1 in self.joined_dict[current_license_number]:
         self.delete_join(current_license_number, -1)
      return self.top_ids[current_license_idx - 1]

   def get_top_ids(self):
      return list(self.joined_dict.keys())

   def get_last_filled(self):
      joined_list = [(k,v) for k,v in self.joined_dict.items()]
      reversed_joined_list = reversed(joined_list)
      empty_item = next((k, v) for k, v in reversed_joined_list if len(v) >= 1)
      index_empty = self.top_ids.index(empty_item[0])
      return self.top_ids[index_empty]

   def invert_dict(self, d):
      return dict([(v, k) for k, v in iter(d.items())])

   def add_join(self, license_id, wm_id):
      with open(self.joined_json_location) as joined_file:
         joined_data = json.load(joined_file)

      wm_ids_at_key = joined_data[license_id]
      if int(wm_id) not in wm_ids_at_key:
         wm_ids_at_key.append(int(wm_id))
         joined_data[license_id] = wm_ids_at_key
         self.joined_dict = joined_data

         with open(self.joined_json_location, 'w') as joined_file:
            json.dump(joined_data, joined_file)

   def add_join_file(self, license_number, wm_id):
      complete_licenses = pd.read_csv("")
      if wm_id != -1:
         store_found = stores[stores['id'] == int(wm_id)]
         store_found['License_no_dash'] = license_number
         license_found = master_licenses[master_licenses['License_no_dash'] == license_number]
         match_found = pd.merge(store_found, license_found, left_on = 'License_no_dash', right_on = 'License_no_dash', how = 'inner')
         licenses_joined = licenses_joined.append(match_found, ignore_index = True, sort = False)


   def delete_join(self, license_id, wm_id):
      with open(self.joined_json_location) as joined_file:
         joined_data = json.load(joined_file)

      wm_ids_at_key = joined_data[license_id]
      wm_ids_at_key.remove(wm_id)

      joined_data[license_id] = wm_ids_at_key
      self.joined_dict = joined_data

      with open(self.joined_json_location, 'w') as joined_file:
         json.dump(joined_data, joined_file)



class JoinSuggestions(Joining):
   def __init__(self, licenses_location, wm_location, joined_json_location, suggestions_location):
      Joining.__init__(self, licenses_location, wm_location, joined_json_location)
      self.suggestions_location = suggestions_location
      self.suggestions = self.read_json(self.suggestions_location)
      self.suggestions_dict = {}

   def read_json(self, filename):
      with open(filename) as data_file:    
         data = json.load(data_file)
      return data

   def get_bottom_ids(self, top_id):
      bottom_ids = []
      if top_id in self.suggestions.keys():
         return [suggestion[0] for suggestion in self.suggestions[top_id]]

      else:
         return self.joined_dict[top_id]

      return bottom_ids

   def get_top_tuple(self,  item_id, top_id = True):
      if top_id:
         return self.getLicenseTuple(item_id)

      else:
         bottom_tuple = self.getWMTuples([item_id])[0]
         return bottom_tuple


   def get_bottom_tuples(self, bottom_ids):
      return self.getWMTuples(bottom_ids)




class Windows(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self, *args, **kwargs)
      self.container = tk.Frame()
      self.container.pack(side = "top", fill = "both", expand = True)
      self.container.grid_rowconfigure(0, weight = 1)
      self.container.grid_columnconfigure(0, weight = 1)
      self.title("Join Licenses")
      self.join_suggestions = JoinSuggestions("..//data//searchResults_clean.csv", "..//data//store.csv", "..//data//latent.json", "..//data//matches.json")
      self.show_frame(self.join_suggestions.get_last_filled())
      #self.show_frame(self.join_suggestions.top_ids[len(self.join_suggestions.top_ids) - 1])

   def show_frame(self, top_id):
      if top_id != -1:
         frame = StoreRecsPage(self.container, self, self.join_suggestions, top_id)
      else:
         frame = LastPage(self.container, self, self.join_suggestions, top_id)
      frame.grid(row = 0, column = 0, sticky = "nsew")
      frame.tkraise()


### INCLUDE EMAIL.
class StoreRecsPage(tk.Frame):
   def __init__(self, parent, controller, JoinSuggestions, top_id):
      tk.Frame.__init__(self, parent)
      self.top_id = top_id
      self.join_suggestions = JoinSuggestions
      self.bottom_ids = self.join_suggestions.get_bottom_ids(self.top_id)
      self.controller = controller
      self.parent = parent
      
      self.label = tk.Label(self, text = "Select the most similar store to the one below. ")
      self.label.pack(pady = 0, padx = 0)

      self._create_top_treeview()
      self._create_bottom_treeview()

      self.progress = ttk.Progressbar(self, orient=HORIZONTAL, length = 500, value = self.progress_location(), maximum = len(self.join_suggestions.top_ids), mode = 'determinate')
      self.progress.pack(fill = 'x', padx=100, pady= 1)

      self.button_next = ttk.Button(self, text = "Next Page", command = lambda: controller.show_frame(self.join_suggestions.traverse_list(top_id)))
      self.button_next.pack(side = RIGHT)


      self.button_back = ttk.Button(self, text = "Previous Page", command = lambda: controller.show_frame(self.join_suggestions.traverse_list(top_id, forward = False)))
      self.button_back.pack(side = LEFT)


   def progress_location(self):
      top_id_location = self.join_suggestions.top_ids.index(self.top_id)
      return top_id_location

   def OnDoubleClick(self, event):
      item = self.treeBottom.identify('item', event.x, event.y)
      wm_id = self.treeBottom.item(item, "text")

      if int(wm_id) not in self.join_suggestions.joined_dict[self.top_id]:
         self.join_suggestions.add_join(self.top_id, wm_id)
         self.rowId = self.treeTop.insert("", 1, text = "Selected", values = self.join_suggestions.get_top_tuple(wm_id, False))

   def DeleteOnDoubleClick(self, event):
      selected_item = self.treeTop.selection()[0] ## get selected item
      item = self.treeTop.identify('item', event.x, event.y)
      wm_id = self.treeTop.item(item, "values")
      print ("clicked on : " + wm_id[0])

      if wm_id[0] != "license":
         self.treeTop.delete(selected_item)
         self.join_suggestions.delete_join(self.top_id, int(wm_id[0]))

   def _create_top_treeview(self):
      top_height = len(self.join_suggestions.joined_dict[self.top_id]) + 2
      self.treeTop = ttk.Treeview(self, height = top_height)
      self.treeTop['columns'] = tuple(self.join_suggestions.licenses_categories)
      self.treeTop['displaycolumns'] = self.join_suggestions.licenses_categories[1:]

      for name in self.join_suggestions.licenses_categories:
         self.treeTop.heading(name, text = name)

      self.treeTop.insert("", 0, text = "", values = self.join_suggestions.get_top_tuple(self.top_id))


      for store_id in self.join_suggestions.joined_dict[self.top_id]:
         if store_id != -1:
            self.treeTop.insert("", 1, text = "Selected", values = self.join_suggestions.get_top_tuple(store_id, False))


      self.treeTop.bind("<Double-1>", self.DeleteOnDoubleClick)
      self.treeTop.pack()

   def _create_bottom_treeview(self):
      self.treeBottom = ttk.Treeview(self)
      self.treeBottom['columns'] = tuple(self.join_suggestions.wm_categories)
      self.treeBottom['displaycolumns'] = self.join_suggestions.wm_categories[1:]

      for name in self.join_suggestions.wm_categories[1:]:
         self.treeBottom.heading(name, text = name)

      index = 0
      bottom_tuples = self.join_suggestions.get_bottom_tuples(self.bottom_ids)

      for bottom_tuple in bottom_tuples:
         self.treeBottom.insert("", index, text = str(bottom_tuple[0]), values = bottom_tuple)
         index += 1

      self.treeBottom.bind("<Double-1>", self.OnDoubleClick)
      self.treeBottom.pack(fill = X)
      self.scrollbar_horizontal_bottom = ttk.Scrollbar(self, orient='horizontal', command = self.treeBottom.xview)    
      self.scrollbar_horizontal_bottom.pack(fill=X)    
      
      self.treeBottom.configure(xscrollcommand=self.scrollbar_horizontal_bottom.set)

class LastPage(tk.Frame):
   def __init__(self, parent, controller, JoinSuggestions, top_id):
      tk.Frame.__init__(self, parent)
      self.top_id = top_id
      self.join_suggestions = JoinSuggestions
      self.controller = controller
      self.parent = parent
      self.label = tk.Label(self, text = "Finished matching licenses and stores. ")
      self.label.pack(pady = 0, padx = 0)

      self.button_back = ttk.Button(self, text = "Previous Page", command = lambda: controller.show_frame(self.join_suggestions.traverse_list(self.join_suggestions.top_ids[len(self.join_suggestions.top_ids) - 1], forward = False)))
      self.button_back.pack(side = LEFT)
      

app = Windows()
app.mainloop()

