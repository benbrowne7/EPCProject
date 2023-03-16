import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp


def addcol(filename, row):
  with open(filename, 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

constit_data = pd.read_csv("constit_data.csv", low_memory=False)
ons2lad = pd.read_csv("ONS2LAD.csv", low_memory=False)

names = []

ons = constit_data['ONS'].tolist()
for o in ons:
  row = ons2lad[ons2lad['LAD20CD'] == o]['LAD20NM']
  if len(row) == 0:
    continue
  else:
    roww = [row.values[0]]
    addcol("constit_names.csv", roww)






  