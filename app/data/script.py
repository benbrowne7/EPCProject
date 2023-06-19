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

df = pd.read_csv("outcode2ons.csv", low_memory=False)


onss = {}

for row in df.itertuples():
  outcode = row[1]
  ons = row[2]
  if ons[0] == 'S' or ons[0] == 'N':
    continue
  if ons not in onss:
    onss[ons] = [outcode]
  else:
    l = onss[ons]
    l.append(outcode)
    onss[ons] = l

for key, val in onss.items():
  l = val
  l.insert(0, key)
  addcol("ons2outcodes", l)

  




  









