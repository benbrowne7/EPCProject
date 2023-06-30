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


northernpow_coords = pd.read_csv("substation_sites_list_northernpow.csv")
northernpow_demand = pd.read_csv("Heat Map Data - Northern-Power-Grid-Demand.csv")

lats = []
lons = []
headrooms = []
drop_indexes = []
for index, row in northernpow_demand.iterrows():
  try:
    headroom = float(row['Firm Capacity']) - float(row['Maximum Demand (MVA)'])
  except:
    headroom = 0
  headrooms.append(headroom)

  id = row['Substation ID']
  id = id.split("-")[0]
  match = northernpow_coords.loc[northernpow_coords['HEATMAP_ID'] == id]
  if match.empty:
    lats.append("na")
    lons.append("na")
    drop_indexes.append(index)
    continue
  e = float(match['EASTING'].values[0])
  n = float(match['NORTHING'].values[0])
  (lat, lon) = OSGB36toWGS84(e,n)
  lats.append(lat)
  lons.append(lon)

northernpow_demand['Demand Headroom (MVA)'] = headrooms
northernpow_demand['lat'] = lats
northernpow_demand['long'] = lons

northernpow_demand = northernpow_demand.drop(drop_indexes, axis=0)


northernpow_demand.to_csv("northern-pow-demand.csv", index=False)







  




  









