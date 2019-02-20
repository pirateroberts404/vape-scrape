import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import pickle
from tempfile import TemporaryFile
import json


class WeedMapStores:
   def __init__(self, wm_location):
      self.wm_location = wm_location
      self.wm_df = pd.read_csv(wm_location)
      self.categories = ['id', 'name', 'city', 'license_type', 'address', 'zip_code', 'phone']
      self.wm_df = self.wm_df[self.categories]

   def getSubset(self, wm_id):
      try:
         return self.wm_df[self.wm_df['id'] == wm_id]
      except:
         print ("Could not find {} indices in licenses_pd").format(wm_id)

   def getTuple(self, wm_id):
      try:
         wm_subset_df = self.getSubset(int(wm_id))
         #tuples = [tuple(x) for x in licenses_subset_pd.values]
         
         return tuple(wm_subset_df.values.tolist()[0])

      except:
         print ("Failed convert tuples. ")



class Licenses:
   def __init__(self, licenses_location):
      self.licenses_location = licenses_location
      self.licenses_df = pd.read_csv(licenses_location)
      self.categories = ['company_name', 'License Number', 'Business Owner',
                        'Business Structure', 'Premise Address', 'Status', 
                        'Expiration Date', 'Adult-Use/Medicinal', 'zip_code',
                        'city', 'email', 'website']
      self.licenses_df = self.licenses_df[self.categories]

   def getSubset(self, licenses_idx):
      try:
         return self.licenses_df.loc[licenses_idx]

      except:
         print ("Could not find {} indices in licenses_pd").format(licenses_idx)

   def getTuple(self, licenses_idx):
      try:
         licenses_subset_df = self.getSubset(licenses_idx)
         #tuple_license = tuple(licenses_subset_df.values)
         tuples = [tuple(x) for x in licenses_subset_df.values]
         return tuples

      except:
         print ("Pending add to file fix. ")

   def getLicenseName(self, license_idx):
      return self.licenses_df['License Number']

   def get_wm_format(self, license_idx):
      return self.licenses_df[['License Number', 'company_name', 'city', 'Adult-Use/Medicinal', 'Premise Address', 'zip_code', 'email']].loc[license_idx]



class JoinSuggestions:
   def __init__(self, filename, licenses, wm_stores):
      self.filename = filename
      self.licenses = licenses
      self.wm_stores = wm_stores
      self.suggestions = self.read_json(filename)

   def read_json(self, filename):
      with open(filename) as data_file:    
         data = json.load(data_file)
      return data

   def get_top_ids(self):
      print(list(self.suggestions.keys()))
      return list(self.suggestions.keys())

   def get_bottom_ids(self, top_id):
      bottom_ids = []
      for suggestion in self.suggestions[top_id]:
         bottom_ids.append(suggestion[0])

      print("bottom ids: " + str(bottom_ids))
      return bottom_ids

   def get_top_tuple(self, top_id):
      return self.wm_stores.getTuple(top_id)
      #return self.licenses.getTuple(top_id)

   def get_bottom_tuples(self, bottom_ids):
      return self.licenses.getTuple(bottom_ids)
      #return self.wm_stores.getTuple(bottom_ids)




class JoinedFile:
   def __init__(self, filename):
      '''
      '''
      self.licenses = Licenses("..//data//searchResultsClean.csv")
      self.wm_stores = WeedMapStores("..//data//store.csv")
      self.join_suggestions = JoinSuggestions("..//data//matches.json", self.licenses, self.wm_stores)

      self.joined_df = self.get_joined_df("joined_matches.txt")


   def addJoined(self, license_idx, store_idx):
      try:
         joined_df = pd.read_pickle(filename)
         joined_df[joined_df['weedmaps_store_id'] == store_idx]['licenses_idx'] = license_idx
         joined_df.to_pickle(filename)

      except:
         print ("failed join. ")


   def get_joined_df(self, filename):
      try:
         return pd.read_pickle(filename)
      except:
         joined_df = pd.DataFrame(columns = {'licenses_idx', 'weedmaps_store_id'})
         joined_df['licenses_idx'] = self.licenses.licenses_df.index.tolist()
         joined_df.to_pickle(filename)
         return joined_df


   def clearFile(self):
      return


   def getIndex(self):
      return

   


class Windows(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self, *args, **kwargs)
      self.container = tk.Frame()
      self.container.pack(side = "top", fill = "both", expand = True)
      self.container.grid_rowconfigure(0, weight = 1)
      self.container.grid_columnconfigure(0, weight = 1)
      self.title("Join Licenses")


      
      self.joined_file = JoinedFile('joined_file.txt')
      self.join_suggestions = self.joined_file.join_suggestions
      self.top_ids = self.join_suggestions.get_top_ids()

      self.frames_dict = {}

      for top_id in self.top_ids:
         bottom_ids = self.join_suggestions.get_bottom_ids(top_id)
         frame = StoreRecsPage(self.container, self, self.top_ids, bottom_ids, top_id, self.joined_file)

         self.frames_dict[top_id] = frame
         frame.grid(row = 0, column = 0, sticky = "nsew")

      self.show_frame(self.top_ids[0])


   def show_frame(self, top_id):
      frame = self.frames_dict[top_id]
      frame.tkraise()



class StoreRecsPage(tk.Frame):
   def __init__(self, parent, controller, top_ids, bottom_ids, top_id, joined_file):
      tk.Frame.__init__(self, parent)

      self.top_ids = top_ids
      self.bottom_ids = bottom_ids
      self.top_id = top_id
      self.joined_file = joined_file
      self.join_suggestions = self.joined_file.join_suggestions
      self.controller = controller
      self.parent = parent
      

      label = tk.Label(self, text = "Select the most similar store to the one below. ")
      label.pack(pady = 0, padx = 0)

      
      self.treeTop = ttk.Treeview(self, height = 2)
      top_column_names = ['id', 'name', 'city', 'license_type', 'address', 'zip_code', 'phone']
      self.treeTop['columns'] = tuple(top_column_names)
      
      for name in top_column_names:
         self.treeTop.heading(name, text = name)

      self.treeTop.insert("", 0, text = "", values = tuple(self.join_suggestions.get_top_tuple(self.top_id)))

      vsb = ttk.Scrollbar(orient="vertical", command=self.treeTop.yview)
      #vsb.pack(side = LEFT)
      #self.treeTop.grid(column=0, row=0, sticky='nsew', in_= parent)
      self.treeTop.pack()
      scrollbar_horizontal = ttk.Scrollbar(self, orient='horizontal', command = self.treeTop.xview)    
      scrollbar_horizontal.pack(fill=X)    
      

      self.treeTop.configure(xscrollcommand=scrollbar_horizontal.set)


      self.treeBottom = ttk.Treeview(self)
      bottom_column_names = ['company_name', 'License Number', 'Business Owner',
                        'Business Structure', 'Premise Address', 'Status', 
                        'Expiration Date', 'Adult-Use/Medicinal', 'zip_code',
                        'city', 'email', 'website']

      self.treeBottom['columns'] = tuple(bottom_column_names)

      for name in bottom_column_names:
         self.treeBottom.heading(name, text = name)

      index = 0
      bottom_tuples = self.join_suggestions.get_bottom_tuples(self.bottom_ids)
      print(bottom_tuples)
      for bottom_id in self.bottom_ids:
         buttom_tuple_idx = self.bottom_ids.index(bottom_id)
         print(bottom_tuples[buttom_tuple_idx])
         self.treeBottom.insert("", index, text = str(bottom_id), values = bottom_tuples[buttom_tuple_idx])
         index += 1

      self.treeBottom.bind("<Double-1>", self.OnDoubleClick)
      self.treeBottom.pack()
      scrollbar_horizontal_bottom = ttk.Scrollbar(self, orient='horizontal', command = self.treeBottom.xview)    
      scrollbar_horizontal_bottom.pack(fill=X)    
      
      self.treeBottom.configure(xscrollcommand=scrollbar_horizontal_bottom.set)

      button_next = ttk.Button(self, text = "Next Page", command = lambda: controller.show_frame(top_ids[top_ids.index(top_id) + 1]))
      button_next.pack(side = RIGHT)


      button_back = ttk.Button(self, text = "Previous Page", command = lambda: controller.show_frame(top_ids[top_ids.index(top_id) - 1]))
      button_back.pack(side = LEFT)

      # progress = tk.Label(self, text = self.get_progress())
      # progress.pack(side = BOTTOM)

   # def get_progress(self):
   #    return "Completed: {}%".format((self.index/len(self.controller.rec_list))*100)

   def OnDoubleClick(self, event):
      item = self.treeBottom.identify('item', event.x, event.y)
      license_idx = self.treeBottom.item(item, "text")
      wm_format_item = self.join_suggestions.licenses.get_wm_format(int(license_idx))
      try:
         self.treeTop.delete(self.rowId)
         self.treeTop.insert("", 1, text = "You selected", values = tuple(wm_format_item))
         self.joined_file.addJoined(license_idx, self.top_id)
         #self.treeTop.insert("", 1, values = ('id', 'name', 'city', 'license_type', 'address', 'zip_code', 'phone'))
      except:
         self.rowId = self.treeTop.insert("", 1, text = "You selected", values = tuple(wm_format_item))


app = Windows()
app.mainloop()

