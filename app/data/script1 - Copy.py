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
df = pd.read_csv("postcode-outcodes.csv", low_memory=False)

for file in os.listdir():
  lats = []
  longs = []
  f = pd.read_csv(file, low_memory=False)
  for row in f.itertuples():
    index = row[0]
    post = row[1]
    x = df.loc[df['postcode'] == post]
    lat = x['latitude']
    long = x['longitude']
    lats.append(lat)
    longs.append(long)
  f['latitude'] = lats
  f['longitude'] = longs
  print(file)


  









