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

ons2lad = pd.read_csv("ONS2LAD.csv", low_memory=False)
os.chdir(sourcedir + "/culmulative_hp")

airdf = pd.read_csv("air-source.csv", low_memory=False)
grounddf = pd.read_csv("ground-source.csv", low_memory=False)

codes = []

for row in airdf.itertuples():
  match = False
  name = row[1]
  name = ''.join(name.split())
  name.replace(",", "")
  for row1 in ons2lad.itertuples():
    ons = row1[1]
    name1 = row1[2]
    if name[0] != name1[0]:
      continue
    name1 = ''.join(name1.split())
    name1.replace(",", "")
    if name == name1:
      codes.append(ons)
      match = True
      break
  if match == False:
    print(name)
    codes.append("NA")

airdf.insert(0, "ONS", codes, False)
grounddf.insert(0, "ONS", codes, False)

airdf.to_csv('airdf-new.csv', index=False)
grounddf.to_csv('grounddf-new.csv', index=False)
  




  









