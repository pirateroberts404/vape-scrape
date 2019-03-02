import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import pickle
from tempfile import TemporaryFile
import json
import time


class WeedMapStores:
   def __init__(self, wm_location):
      self.wm_location = wm_location
      self.wm_df = pd.read_csv(wm_location)
      # Add a license number category.
      self.wm_df = self.wm_df.rename(index = str, columns = {'id': 'id', 'name': 'Name', 'address': 'Address', 'city': 'City', 
                                                         'zip_code': 'Zip Code', 'phone' : 'Phone Number', 'license_type' : 'Adult-Use/Medicinal',
                                                          'web_url': 'WeedMaps URL', 'retailer_services' : 'Services'})
      self.wm_categories = ['id', 'Name', 'Address', 'City', 'Zip Code', 'Phone Number', 'Adult-Use/Medicinal', 'WeedMaps URL', 'Services']
      self.wm_df = self.wm_df[self.wm_categories]

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
      self.licenses_df = pd.read_csv(licenses_location)
      self.licenses_df['id'] = "license"
      self.licenses_df = self.licenses_df.rename(index = str, columns = {'company_name' : 'Name', 'Premise Address' : 'Address', 
                                                                        'city' : 'City', 'zip_code' : 'Zip Code', 'phone' : 'Phone Number', 'Adult-Use/Medicinal':  'Adult-Use/Medicinal',
                                                                        'website': 'Web URL', 'License Type': 'License Type', 'Business Owner' : 'Business Owner', 'License Number' : 'License Number'})
      self.licenses_categories = ['id', 'Name', 'Address', 'City', 'Zip Code', 'Phone Number', 'Adult-Use/Medicinal', 'Web URL', 'License Type', 'Business Owner', 'License Number']
      self.licenses_df = self.licenses_df[self.licenses_categories]
      self.licenses_df['License Number'] = self.licenses_df['License Number'].str.replace("-", "")
      

   def getLicenseTuple(self, license_number):
      try:
         print("license number: " + license_number)
         top_tuple = tuple(self.licenses_df[self.licenses_df['License Number'] == license_number].values[0])
         return top_tuple

      except:
         print ("Could find license number {} ".format(license_number))

   
class JoinedFile(Licenses, WeedMapStores):
   def __init__(self, licenses_location, wm_location, joined_location):
      Licenses.__init__(self, licenses_location)
      WeedMapStores.__init__(self, wm_location)
      self.joined_location = joined_location
      self.joined_dict = self.get_joined_dictionary(self.joined_location)
      self.top_ids = self.get_top_ids()

   def get_joined_dictionary(self, joined_location):
      with open (joined_location) as joined_file:
         joined_data = json.load(joined_file)

      return joined_data

   def traverse_list(self, current_license_number, forward = True):
      current_license_idx = self.top_ids.index(current_license_number)
      if forward:
         return self.top_ids[current_license_idx + 1]
      return self.top_ids[current_license_idx - 1]

   def update_list(self, current_license_number):
      joined_updated = self.get_joined_dictionary(self.joined_location)
      return joined_updated[current_license_number]

   def get_top_ids(self):
      return list(self.joined_dict.keys())

   def get_last_filled(self):
      empty_item = next((k, v) for k, v in self.joined_dict.items() if len(v) < 1)
      index_empty = self.top_ids.index(empty_item[0])
      return self.top_ids[index_empty - 1]

   def add_join(self, license_id, wm_id):
      with open(self.joined_location) as joined_file:
         joined_data = json.load(joined_file)

      wm_ids_at_key = joined_data[license_id]
      wm_ids_at_key.append(int(wm_id))

      joined_data[license_id] = wm_ids_at_key

      with open(self.joined_location, 'w') as joined_file:
         json.dump(joined_data, joined_file)

   def delete_join(self, license_id, wm_id):
      with open(self.joined_location) as joined_file:
         joined_data = json.load(joined_file)

      wm_ids_at_key = joined_data[license_id]
      wm_ids_at_key.remove(wm_id)

      joined_data[license_id] = wm_ids_at_key

      with open(self.joined_location, 'w') as joined_file:
         json.dump(joined_data, joined_file)



class JoinSuggestions(JoinedFile):
   def __init__(self, licenses_location, wm_location, joined_location, suggestions_location):
      JoinedFile.__init__(self, licenses_location, wm_location, joined_location)
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
      self.join_suggestions = JoinSuggestions("..//data//searchResultsClean.csv", "..//data//store.csv", "latent.json", "clean_matches.json")
      self.show_frame(self.join_suggestions.get_last_filled())


   def show_frame(self, top_id):
      frame = StoreRecsPage(self.container, self, self.join_suggestions, top_id)
      frame.grid(row = 0, column = 0, sticky = "nsew")
      frame.tkraise()


class StoreRecsPage(tk.Frame):
   def __init__(self, parent, controller, JoinSuggestions, top_id):
      tk.Frame.__init__(self, parent)
      self.top_id = top_id
      self.join_suggestions = JoinSuggestions
      self.bottom_ids = self.join_suggestions.get_bottom_ids(self.top_id)
      self.controller = controller
      self.parent = parent
      
      label = tk.Label(self, text = "Select the most similar store to the one below. ")
      label.pack(pady = 0, padx = 0)

      

      self.treeTop = ttk.Treeview(self, height = 2)
        
      self.treeTop['columns'] = tuple(self.join_suggestions.licenses_categories)
      self.treeTop['displaycolumns'] = self.join_suggestions.licenses_categories[1:]
      
      for name in self.join_suggestions.licenses_categories:
         self.treeTop.heading(name, text = name)

      
      self.treeTop.insert("", 0, text = "", values = self.join_suggestions.get_top_tuple(self.top_id))
      self.add_file_top()
      self.treeTop.bind("<Double-1>", self.DeleteOnDoubleClick)
      self.treeTop.pack()

      scrollbar_horizontal = ttk.Scrollbar(self, orient='horizontal', command = self.treeTop.xview)    
      scrollbar_horizontal.pack(fill=X)    
      self.treeTop.configure(xscrollcommand=scrollbar_horizontal.set)


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
      scrollbar_horizontal_bottom = ttk.Scrollbar(self, orient='horizontal', command = self.treeBottom.xview)    
      scrollbar_horizontal_bottom.pack(fill=X)    
      
      self.treeBottom.configure(xscrollcommand=scrollbar_horizontal_bottom.set)


      self.progress = ttk.Progressbar(self, orient=HORIZONTAL, length = 500, value = self.progress_location(), maximum = len(self.join_suggestions.top_ids), mode = 'determinate')
      self.progress.pack(fill = 'x', padx=100, pady= 1)

      button_next = ttk.Button(self, text = "Next Page", command = lambda: controller.show_frame(self.join_suggestions.traverse_list(top_id)))
      button_next.pack(side = RIGHT)


      button_back = ttk.Button(self, text = "Previous Page", command = lambda: controller.show_frame(self.join_suggestions.traverse_list(top_id, forward = False)))
      button_back.pack(side = LEFT)


   def progress_location(self):
      top_id_location = self.join_suggestions.top_ids.index(self.top_id)
      return top_id_location

   def add_file_top(self):
      top_tuples = self.join_suggestions.update_list(self.top_id)
      if len(top_tuples) > 0: 
         for wm_id in top_tuples:
            print ("wm_id: " + str(wm_id))
            self.treeTop.insert("", 1, text = "Selected", values = self.join_suggestions.get_top_tuple(wm_id, False))


   def OnDoubleClick(self, event):
      item = self.treeBottom.identify('item', event.x, event.y)
      wm_id = self.treeBottom.item(item, "text")
      self.join_suggestions.add_join(self.top_id, wm_id)


      try:
         self.treeTop.delete(self.rowId)
      except:
         pass
      
      self.rowId = self.treeTop.insert("", 1, text = "Selected", values = self.join_suggestions.get_top_tuple(wm_id, False))


   def DeleteOnDoubleClick(self, event):
      selected_item = self.treeTop.selection()[0] ## get selected item
      item = self.treeTop.identify('item', event.x, event.y)
      wm_id = self.treeTop.item(item, "values")
      print ("clicked on : " + wm_id[0])

      if wm_id[0] != "license":
         self.treeTop.delete(selected_item)
         self.join_suggestions.delete_join(self.top_id, int(wm_id[0]))
      

app = Windows()
app.mainloop()

