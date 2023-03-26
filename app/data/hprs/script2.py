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

epc_list = []
hpr_list = []

for file in os.listdir(sourcedir):
  print(file)
  if file[0] != 'd':
    continue
  data = pd.read_csv(file, low_memory=False)
  epcs = data.iloc[:,0].tolist()
  hprs = data.iloc[:,1].tolist()
  epc_mean = np.mean(epcs)
  hpr_mean = np.mean(hprs)
  epc_list.append(epc_mean)
  hpr_list.append(hpr_mean)

print(len(epc_list), np.mean(epc_list))
print(len(hpr_list), np.mean(hpr_list))










  