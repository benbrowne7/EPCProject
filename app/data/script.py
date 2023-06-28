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

os.chdir(sourcedir + "/Reduced/Reduced_smallest")
for file in os.listdir('.'):
  df = pd.read_csv(file)
  file1 = file[:-10]
  hprs = pd.read_csv(sourcedir + "/hprs/" + file1 + "hprs.csv")
  print(hprs.iloc[:,1])


  




  









