import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp


def addcol(filename, row):
  with open(filename + "hprs.csv", 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

l1 = []
l2 = []
l3 = []
l4 = []


constit_data = pd.read_csv("constit_data.csv", low_memory=False)
ons2lad = pd.read_csv("ONS2LAD.csv", low_memory=False)

largest_epc = constit_data.nlargest(5, 'EPC_MEAN', keep='all')
largest_epc = largest_epc['ONS'].tolist()
smallest_epc = constit_data.nsmallest(5, 'EPC_MEAN', keep='all')
smallest_epc = smallest_epc['ONS'].tolist()

largest_hpr = constit_data.nlargest(5, 'HPR_MEAN', keep='all')
largest_hpr = largest_hpr['ONS'].tolist()
smallest_hpr = constit_data.nsmallest(5, 'HPR_MEAN', keep='all')
smallest_hpr = smallest_hpr['ONS'].tolist()

for ons in largest_epc:
  name = ons2lad[ons2lad['LAD20CD'] == ons]['LAD20NM']
  if len(name) == 0:
    continue
  else:
    l1.append(name.values[0])

for ons in smallest_epc:
  name = ons2lad[ons2lad['LAD20CD'] == ons]['LAD20NM']
  if len(name) == 0:
    continue
  else:
    l2.append(name.values[0])

for ons in largest_hpr:
  name = ons2lad[ons2lad['LAD20CD'] == ons]['LAD20NM']
  if len(name) == 0:
    continue
  else:
    l3.append(name.values[0])

for ons in smallest_hpr:
  name = ons2lad[ons2lad['LAD20CD'] == ons]['LAD20NM']
  if len(name) == 0:
    continue
  else:
    l4.append(name.values[0])
  
  
print(l1)
print(l2)
print(l3)
print(l4)


  



  