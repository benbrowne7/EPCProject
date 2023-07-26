import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp
import shutil
from collections import defaultdict


def addcol(filename, row):
  with open(filename, 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)


os.chdir(sourcedir + "/Reduced/Reduced_final")
for file in os.listdir('.'):
  print(file)
  ons = file.split("-")[1]
  district_mean = defaultdict(int)
  district_count = defaultdict(int)
  district_hpr = defaultdict(int)
  
  
  
  df = pd.read_csv(file)
  for row in df.itertuples(index=False):
    outcode = row[0].split(" ")[0]
    if outcode[-1].isalpha() == True:
      district = outcode[:-1]
    else:
      district = outcode

    district_mean[district] += row[1]
    district_count[district] += 1
    district_hpr[district] += row[7]

  os.chdir(sourcedir + "/Postcode-Data/" + ons)

  #make outcode csvs
  addcol("district_data.csv", ['district', 'epc', 'hpr'])
  for key, val in district_mean.items():
    epc_mean = round(val / district_count[key],1)
    hpr_mean = round(district_hpr[key] / district_count[key], 2)
    row = [key, epc_mean, hpr_mean]
    addcol("district_data.csv", row)
    
  

  os.chdir(sourcedir + "/Reduced/Reduced_final")




    





  


  



  