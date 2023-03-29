import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp


def addcol(filename, row):
  with open(filename + ".csv", 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

os.chdir(sourcedir + "/postcode_data")
coords = pd.read_csv("postcode-outcodes.csv", low_memory=False)

os.chdir(sourcedir + "/Reduced")
for file in os.listdir():
  os.chdir(sourcedir + "/Reduced")
  print(file)
  post_mean = defaultdict(int)
  post_count = defaultdict(int)
  post_hpr = defaultdict(int)
  df = pd.read_csv(file, low_memory=False)
  os.chdir(sourcedir + "/hprs")
  hprs = pd.read_csv(file[:-10] + "hprs.csv")
  for row in df.itertuples():
    index = row[0]
    post = row[2].split(" ")[0]
    post_mean[post] += row[3]
    post_count[post] += 1
    post_hpr[post] += hprs.iat[index-1,1]
  os.chdir(sourcedir + "/postcode_data")
  addcol(file[:-10] + "-postcode", ['postcode', 'epc', 'hpr', 'lat', 'long'])
  for key, val in post_mean.items():
    epc_mean = round(val / post_count[key],1)
    hpr_mean = round(post_hpr[key] / post_count[key], 2)
    x = coords.loc[coords['postcode'] == key]
    if x.empty:
      lat = "nan"
      long = "nan"
    else:
      lat = x['latitude'].values[0]
      long = x['longitude'].values[0]
    row = [key, epc_mean, hpr_mean, lat, long]
    print(row)
    addcol(file[:-10] + "-postcode", row)









