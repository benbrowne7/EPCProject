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
  name = row[0]
  name.replace(" ", "-")
  name.replace(",", "-")
  for row1 in ons2lad.itertuples():
    ons = row1[0]
    name1 = row1[1]
    name1.replace(" ", "-")
    name1.replace(",", "-")
    print(name, name1)
    if name == name1:
      codes.append(ons)
      break
  codes.append("NA")

print(codes)
  




  









