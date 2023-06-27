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


#scottishpow = pd.read_csv("distributed-generation-sp-distribution-heat-maps-spd-primary-substations.csv", low_memory=False)
northwestpow = pd.read_csv("distribution-substation-headroom-northwest.csv", low_memory=True)
powernetworks = pd.read_csv("ukpn_primary_postcode_area.csv", low_memory=True)
nationalgrid = pd.read_csv("WPD Network Capacity Map 19-06-2023", low_memory=False)




northwestpow_dict = {}
powernetworks_dict = {}
nationalgrid_dict = {}


for index, row in northwestpow.iterrow():
  sub_name = row[0]
  



  




  









