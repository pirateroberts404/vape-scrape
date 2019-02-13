import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import pickle
from tempfile import TemporaryFile


class LoadStores:
   def __init__(self, rec_list):
      self.rec_list = rec_list
      self.wp_stores_df = pd.read_csv("..//data//weedmaps_not_joined.csv")
      self.licenses_df = pd.read_csv("..//data//searchResults.csv")


   def wp_store_info(self, storeId):
      single_store = self.wp_stores_df[self.wp_stores_df['id'] == storeId]
      name = single_store['name'].values[0]
      address = single_store['address'].values[0]
      phone = single_store['phone'].values[0]
      service = single_store['retailer_services'].values[0]
      store_string = "Name: {}\nAddress: {}\nPhone: {}\nRetailer Service: {}".format(name, address, phone, service)
      return store_string

   def license_info(self, license_index):
      try:
         list_info = self.licenses_df['Business Contact Information'].values[license_index].split(':')
         name = list_info[0]
         phone = list_info[2]
         address = self.licenses_df['Premise Address'].values[license_index]
         license_string = 'Name- ' + name + ',' + phone + ', Address- ' + address
         return license_string

      except:
         list_info = self.licenses_df['Business Contact Information'].values[license_index]
         address = self.licenses_df['Premise Address'].values[license_index]
         license_string = license_info + 'Address- ' + address
         return license_string

   def list_licenses_info(self, list_indices):
      licenses_strings = []
      for index in list_indices:
         licenses_strings.append(self.license_info(index))

      return licenses_strings



class Windows(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self, *args, **kwargs)
      container = tk.Frame(self)
      container.pack(side = "top", fill = "both", expand = True)
      container.grid_rowconfigure(0, weight = 2)
      container.grid_columnconfigure(0, weight = 2)
      self.frames_dict = {}
      self.rec_list = self.load_data()
      self.stores_data = LoadStores(self.rec_list)

      for rec in self.rec_list:
         index = self.rec_list.index(rec)
         frame = StoreRecsPage(container, self, rec[0], rec[1], index)
         self.frames_dict[frame.storeId] = frame
         frame.grid(row = 0, column = 0, sticky = "nsew")

      self.show_frame(50268)

   def load_data(self):
      with open('rec_list.txt', 'rb') as fb:
         rec_list = pickle.load(fb)
      return rec_list

   def show_frame(self, StoreId, Combobox = "None"):
      if Combobox != "None":
         print(Combobox.get())
      frame = self.frames_dict[StoreId]
      frame.tkraise()



class StoreRecsPage(tk.Frame):
   def __init__(self, parent, controller, storeId, recs, index):
      self.storeId = storeId
      self.recs = recs
      self.index = index
      self.controller = controller
      self.licenses = controller.stores_data.list_licenses_info(recs)
      self.licenses.append('None of the above.')

      tk.Frame.__init__(self, parent)

      label = tk.Label(self, text = controller.stores_data.wp_store_info(storeId))
      label.pack(pady = 0, padx = 0)

      progress = tk.Label(self, text = self.get_progress())
      progress.pack(side = BOTTOM)

      combo1 = ttk.Combobox(self)
      combo1['values'] = tuple(self.licenses)
      combo1.current(len(self.licenses) - 1)
      combo1.pack(side = TOP, fill = X, expand = True)

      button_next = ttk.Button(self, text = "Next Page", command = lambda: controller.show_frame(controller.rec_list[index + 1][0], combo1))
      button_next.pack(side = RIGHT)
      if combo1.get() != 'None of the above.':
         print(combo1.get())


      button_back = ttk.Button(self, text = "Previous Page", command = lambda: controller.show_frame(controller.rec_list[index - 1][0], combo1))
      button_back.pack(side = LEFT)

   def get_progress(self):
      return "Completed: {}%".format((self.index/len(self.controller.rec_list))*100)



app = Windows()
app.mainloop()

