import json
import os
from datetime import datetime, timedelta
import numpy as np
from numpy import interp
import pandas as pd


abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)



def organizedata(data):
    location = {}
    ratings = {}
    property = {}
    features = {}
    location['address1'] = data['address1']
    location['postcode'] = data['postcode']
    location['county'] = data['county']
    location['local'] = data['local-authority']
    ratings['current'] = data['current-energy-rating']
    ratings['current-int'] = data['current-energy-efficiency']
    ratings['band'] = [int(ratings['current-int'])-5, int(ratings['current-int'])+5]
    property['type'] = data['property-type']
    property['form'] = data['built-form']
    property['tenure'] = data['tenure']
    property['date'] = data['lodgement-date']
    x = data['construction-age-band']
    if "England" in x:
        x = x[18:]
    property['age'] = x
    features['multi-glaze'] = data['multi-glaze-proportion']
    features['windows'] = data['windows-description']
    features['windows-rate'] = data['windows-energy-eff']
    features['floors'] = data['floor-description']
    features['floors-rate'] = data['floor-energy-eff']
    features['hot-water'] = data['hotwater-description']
    features['walls'] = data['walls-description']
    features['walls-rate'] = data['walls-energy-eff']
    features['roof'] = data['roof-description']
    features['roof-rate'] = data['roof-energy-eff']
    features['mainheat'] = data['mainheat-description']
    features['mainheat-rate'] = data['mainheat-energy-eff']
    features['mainfuel'] = data['main-fuel']
    return location, ratings, property, features

def determineimprovement(text):
    if "double" in text and ("glazed" or "glazing") in text:
        return "Double Glazing"
    if "wall" in text and "insulation" in text:
        return "Wall Insulation"
    if "draught" in text and "proofing" in text:
        return "Draught Proofing"
    else:
        return "Unable to resolve recommendation"

def checkdates(cert_date, current_date):
    year = int(current_date[:4]) - 10
    if int(cert_date[:4]) < year:
        return False
    if int(cert_date[:4] == year):
        if int(cert_date[5:7]) < int(current_date[5:7]):
            return False
        if int(cert_date[5:7]) == int(current_date[5:7]):
            if int(cert_date[8:10] < int(current_date[8:10])):
                return False
    return True

def heatpumpready(ratings, features):
    f = []
    scores = []
    f.append(features['walls-rate'])
    f.append(features['roof-rate'])
    f.append(features['windows-rate'])
    f.append(features['floors-rate'])
    for weight in f:
        if weight == 'Very Poor':
            scores.append(10)
            continue
        if weight == 'Poor':
            scores.append(6)
            continue
        if weight == ('Average' or 'N/A'):
            scores.append(3)
            continue
        if weight == 'Good':
            scores.append(1)
            continue
        if weight == 'Very Good':
            scores.append(0)
            continue
        else:
            scores.append(3)
            continue
    score = scores[0]*2 + scores[1]*2 + scores[2] + scores[3]
    rating = int(ratings['current-int'])
    if rating > 100:
        rating = 100
    scorex = interp(rating, [0,100], [10,0])
    score += scorex
    hpr = round(interp(score, [0,70], [1.2,0.2]), 2)
    if hpr >= 1.1:
        tag = 'Strong Candidate'
        return round(hpr,2), tag
    if hpr >= 1:
        tag = 'Good Candidate'
        return round(hpr,2), tag
    if hpr >= 0.7:
        tag = 'Some Improvements Needed'
        return round(hpr,2), tag
    else:
        tag = "Major Improvements Needed"
        return round(hpr,2), tag

def percentilecolours(index_x, index_x1):
    if index_x in [0,1,2]:
        tag1 = 0
    if index_x in [3,4,5,6]:
        tag1 = 1
    if index_x in [7,8,9]:
        tag1 = 2
    if index_x1 in [0,1,2]:
        tag2 = 0
    if index_x1 in [3,4,5,6]:
        tag2 = 1
    if index_x1 in [7,8,9]:
        tag2 = 2
    return tag1, tag2

def findpositioninpercentile(rate1, percentile1, rate2, percentile2):
    if rate1 > percentile1[8]:
        index_x = 9
    else:
        for i in range(0,len(percentile1)):
          if rate1 <= percentile1[i]:
            index_x = i
            break

    if rate2 > percentile2[8]:
        index_x1 = 9
    else:
        for i in range(0,len(percentile2)):
            if rate2 <= percentile2[i]:
                index_x1 = i
                break
    return index_x, index_x1

def findpercentileforLAD():
    abspath = os.path.abspath(__file__)
    sourcedir = os.path.dirname(abspath)
    all_constits = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)
    all_mean_epcs = all_constits['EPC_MEAN'].tolist()
    all_mean_hprs = all_constits['HPR_MEAN'].tolist()
    percentile_epc = np.percentile(all_mean_epcs, [10,20,30,40,50,60,70,80,90])
    percentile_hpr = np.percentile(all_mean_hprs, [10,20,30,40,50,60,70,80,90])
    return percentile_epc, percentile_hpr

def singleladrequest(ons, av_yoy):
    getname = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    row = getname[getname['LAD20CD'] == ons]
    name = row['LAD20NM'].values[0]
    l = name.split(" ")
    if len(l) != 1:
        name = '-'.join(l)

    filename = "domestic-" + ons + "-" + name + "hprs.csv"

    data = pd.read_csv(sourcedir + "/data/hprs/" + filename, low_memory=False)

    #epc/hpr data for specific LAD
    epcs = data.iloc[:,0].tolist()
    hprs = data.iloc[:,1].tolist()
    epc_mean = int(np.mean(epcs))
    hpr_mean = round(np.mean(hprs), 2)
    n_over1 = 0
    total = len(hprs)
    for x in hprs:
        if x > 1.0:
            n_over1 += 1
    proportion = int(float(n_over1/total)*100)
    percentile_epc, percentile_hpr = findpercentileforLAD()
    index_x, index_x1 = findpositioninpercentile(epc_mean, percentile_epc, hpr_mean, percentile_hpr)
    tag1, tag2 = percentilecolours(index_x, index_x1)
    epc_string1 = "Mean EPC for {} is [{}] w/ av. y/y increase of {}".format(name, epc_mean, av_yoy)
    hpr_string1 = "Mean HPR rating for {} is [{}]".format(name, hpr_mean)
    epc_string2 = "{} is within the {}th -> {}th percentile for Local Authority Districts (EPC)".format(name, index_x*10, (index_x+1)*10)
    hpr_string2 = "{} is within the {}th -> {}th percentile for Local Authority Districts (HPR)".format(name , index_x1*10, (index_x1+1)*10)
    proportion_string = "{}% of dwellings have a HPR rating of over 1 (good candidates)".format(proportion)

    return epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1

def getconstitnames():
    constit_names = pd.read_csv(sourcedir + "/data/constit_names.csv", low_memory=False)
    names = constit_names['NAMES'].tolist()
    names.sort()
    return names

