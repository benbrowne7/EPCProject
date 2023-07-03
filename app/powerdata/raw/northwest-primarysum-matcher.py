import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp
from bng_latlon import WGS84toOSGB36
from bng_latlon import OSGB36toWGS84


def addcol(filename, row):
  with open(filename + ".csv", 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)


northwest_distribution = pd.read_csv("distribution-substation-headroom-northwest.csv")
northwest_substations = pd.read_csv("enwl-substation.csv")

primary_subs_dict = {}

for index, row in northwest_distribution.iterrows():
  primary_sub_name = row['Primary_sub_name'].split("(")[0]
  primary_sub_id = row['Primary_sub_name'].split("(")[1][:-1]
  capacity = float(row['substation_capacity_kva']) / 1000
  demand = float(row['total_load_kva']) / 1000
  headroom = float(row['headroom_kva']) / 1000
  if primary_sub_id not in primary_subs_dict:
    primary_subs_dict[primary_sub_id] = [primary_sub_name, primary_sub_id, capacity, demand, headroom]
  else:
    l = primary_subs_dict[primary_sub_id]
    capacity = l[2] + capacity
    demand = l[3] + demand
    headroom = l[4] + headroom
    primary_subs_dict[primary_sub_id] = [primary_sub_name, primary_sub_id, capacity, demand, headroom]
  
unmatch = 0
for key, val in primary_subs_dict.items():
  row = northwest_substations.loc[northwest_substations['NUMBER'] == key]
  if row.empty:
    continue
  point = row['Geo Point'].values[0]
  lat = point.split(',')[0]
  long = point.split(',')[1]
  val.append(lat)
  val.append(long)
  primary_subs_dict[key] = val

new_df = pd.DataFrame.from_dict(primary_subs_dict, orient='index', columns=['Substation Name', 'ID', 'Firm Capacity (MVA)', 'Peak Demand (MVA)', 'Headroom (MVA)', 'Latitude', 'Longitude'])
new_df.to_csv("northwest_elec-demand.csv", index=False)



  
    








#northernpow_demand.to_csv("northern-pow-demand.csv", index=False)







  




  









