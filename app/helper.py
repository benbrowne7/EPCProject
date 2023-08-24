import json
import os
from datetime import datetime, timedelta
import numpy as np
from numpy import interp
import pandas as pd
import math
import re
from pathlib import Path
import arrow


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
    property['floor-area'] = data['total-floor-area']
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

    for file in os.listdir(sourcedir + "/data/hprs/"):
        if ons in file:
            os.chdir(sourcedir + "/data/hprs/")
            data = pd.read_csv(file)
            break
    os.chdir(sourcedir)


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

def extractsubstationinfo(valid_substations):
    #[sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "DNO"]
    num_substations = len(valid_substations)
    total_capacity = 0
    total_headroom = 0
    invalid = 0
    for key, val in valid_substations.items():
        if math.isnan(val[6]):
            invalid += 1
            continue
        total_capacity += float(val[5])
        total_headroom += float(val[6])
        dno = val[9]
    utilization = round(((total_capacity - total_headroom) / total_capacity * 100),1)
    if dno == 'Electricity North West':
        total_capacity = 0
        utilization = 0
    return num_substations, round(total_capacity,2), round(total_headroom,2), utilization, dno
    


def getconstitnames():
    #constit = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    #names = []
    #for row in constit.itertuples():
        #index = row[0]
        #ons = row[1]
        #name = row[2]
        #if ons[0] == 'E' or ons[0] == 'W':
           # names.append(name)
    #names.sort()
    names = ['Adur', 'Allerdale', 'Amber Valley', 'Arun', 'Ashfield', 'Ashford', 'Babergh', 'Barking and Dagenham', 'Barnet', 'Barnsley', 'Barrow-in-Furness', 'Basildon', 'Basingstoke and Deane', 'Bassetlaw', 'Bath-and-North-East-Somerset', 'Bedford', 'Bexley', 'Birmingham', 'Blaby', 'Blackburn-with-Darwen', 'Blackpool', 'Blaenau Gwent', 'Bolsover', 'Bolton', 'Boston', 'Bournemouth, Christchurch and Poole', 'Bracknell-Forest', 'Bradford', 'Braintree', 'Breckland', 'Brent', 'Brentwood', 'Bridgend', 'Brighton-and-Hove', 'Bristol-City-of', 'Broadland', 'Bromley', 'Bromsgrove', 'Broxbourne', 'Broxtowe', 'Buckinghamshire', 'Burnley', 'Bury', 'Caerphilly', 'Calderdale', 'Cambridge', 'Camden', 'Cannock Chase', 'Canterbury', 'Cardiff', 'Carlisle', 'Carmarthenshire', 'Castle Point', 'Central Bedfordshire', 'Ceredigion', 'Charnwood', 'Chelmsford', 'Cheltenham', 'Cherwell', 'Cheshire East', 'Cheshire West and Chester', 'Chesterfield', 'Chichester', 'Chorley', 'City of London', 'Colchester', 'Conwy', 'Copeland', 'Corby', 'Cornwall', 'Cotswold', 'County Durham', 'Coventry', 'Craven', 'Crawley', 'Croydon', 'Dacorum', 'Darlington', 'Dartford', 'Daventry', 'Denbighshire', 'Derby', 'Derbyshire Dales', 'Doncaster', 'Dorset', 'Dover', 'Dudley', 'Ealing', 'East Cambridgeshire', 'East Devon', 'East Hampshire', 'East Hertfordshire', 'East Lindsey', 'East Northamptonshire', 'East Staffordshire', 'East Suffolk', 'East-Riding-of-Yorkshire', 'Eastbourne', 'Eastleigh', 'Eden', 'Elmbridge', 'Enfield', 'Epping Forest', 'Epsom and Ewell', 'Erewash', 'Exeter', 'Fareham', 'Fenland', 'Flintshire', 'Folkestone and Hythe', 'Forest of Dean', 'Fylde', 'Gateshead', 'Gedling', 'Gloucester', 'Gosport', 'Gravesham', 'Great Yarmouth', 'Greenwich', 'Guildford', 'Gwynedd', 'Hackney', 'Halton', 'Hambleton', 'Hammersmith and Fulham', 'Harborough', 'Haringey', 'Harlow', 'Harrogate', 'Harrow', 'Hart', 'Hartlepool', 'Hastings', 'Havant', 'Havering', 'Herefordshire-County-of', 'Hertsmere', 'High Peak', 'Hillingdon', 'Hinckley and Bosworth', 'Horsham', 'Hounslow', 'Huntingdonshire', 'Hyndburn', 'Ipswich', 'Isle of Anglesey', 'Isle of Wight', 'Isles of Scilly', 'Islington', 'Kensington and Chelsea', 'Kettering', "King's Lynn and West Norfolk", 'Kingston upon Thames', 'Kingston-upon-Hull-City-of', 'Kirklees', 'Knowsley', 'Lambeth', 'Lancaster', 'Leeds', 'Leicester', 'Lewes', 'Lewisham', 'Lichfield', 'Lincoln', 'Liverpool', 'Luton', 'Maidstone', 'Maldon', 'Malvern Hills', 'Manchester', 'Mansfield', 'Medway', 'Melton', 'Mendip', 'Merthyr Tydfil', 'Merton', 'Mid Devon', 'Mid Suffolk', 'Mid Sussex', 'Middlesbrough', 'Milton-Keynes', 'Mole Valley', 'Monmouthshire', 'Neath Port Talbot', 'New Forest', 'Newark and Sherwood', 'Newcastle upon Tyne', 'Newcastle-under-Lyme', 'Newham', 'Newport', 'North Devon', 'North East Derbyshire', 'North Hertfordshire', 'North Kesteven', 'North Norfolk', 'North Tyneside', 'North Warwickshire', 'North West Leicestershire', 'North-East-Lincolnshire', 'North-Lincolnshire', 'North-Somerset', 'Northampton', 'Northumberland', 'Norwich', 'Nottingham', 'Nuneaton and Bedworth', 'Oadby and Wigston', 'Oldham', 'Oxford', 'Pembrokeshire', 'Pendle', 'Peterborough', 'Plymouth', 'Portsmouth', 'Powys', 'Preston', 'Reading', 'Redbridge', 'Redcar-and-Cleveland', 'Redditch', 'Reigate and Banstead', 'Rhondda Cynon Taf', 'Ribble Valley', 'Richmond upon Thames', 'Richmondshire', 'Rochdale', 'Rochford', 'Rossendale', 'Rother', 'Rotherham', 'Rugby', 'Runnymede', 'Rushcliffe', 'Rushmoor', 'Rutland', 'Ryedale', 'Salford', 'Sandwell', 'Scarborough', 'Sedgemoor', 'Sefton', 'Selby', 'Sevenoaks', 'Sheffield', 'Shropshire', 'Slough', 'Solihull', 'Somerset West and Taunton', 'South Cambridgeshire', 'South Derbyshire', 'South Hams', 'South Holland', 'South Kesteven', 'South Lakeland', 'South Norfolk', 'South Northamptonshire', 'South Oxfordshire', 'South Ribble', 'South Somerset', 'South Staffordshire', 'South Tyneside', 'South-Gloucestershire', 'Southampton', 'Southend-on-Sea', 'Southwark', 'Spelthorne', 'St Albans', 'St. Helens', 'Stafford', 'Staffordshire Moorlands', 'Stevenage', 'Stockport', 'Stockton-on-Tees', 'Stoke-on-Trent', 'Stratford-on-Avon', 'Stroud', 'Sunderland', 'Surrey Heath', 'Sutton', 'Swale', 'Swansea', 'Swindon', 'Tameside', 'Tamworth', 'Tandridge', 'Teignbridge', 'Telford-and-Wrekin', 'Tendring', 'Test Valley', 'Tewkesbury', 'Thanet', 'Three Rivers', 'Thurrock', 'Tonbridge and Malling', 'Torbay', 'Torfaen', 'Torridge', 'Tower Hamlets', 'Trafford', 'Tunbridge Wells', 'Uttlesford', 'Vale of Glamorgan', 'Vale of White Horse', 'Wakefield', 'Walsall', 'Waltham Forest', 'Wandsworth', 'Warrington', 'Warwick', 'Watford', 'Waverley', 'Wealden', 'Wellingborough', 'Welwyn Hatfield', 'West Devon', 'West Lancashire', 'West Lindsey', 'West Oxfordshire', 'West Suffolk', 'West-Berkshire', 'Westminster', 'Wigan', 'Wiltshire', 'Winchester', 'Windsor-and-Maidenhead', 'Wirral', 'Woking', 'Wokingham', 'Wolverhampton', 'Worcester', 'Worthing', 'Wrexham', 'Wychavon', 'Wyre', 'Wyre Forest', 'York']
    return names

def getconstitnames_shp():
    constit22 = ['Adur', 'Allerdale', 'Amber Valley', 'Arun', 'Ashfield', 'Ashford', 'Babergh', 'Barking and Dagenham', 'Barnet', 'Barnsley', 'Barrow-in-Furness', 'Basildon', 'Basingstoke and Deane', 'Bassetlaw', 'Bath and North East Somerset', 'Bedford', 'Bexley', 'Birmingham', 'Blaby', 'Blackburn with Darwen', 'Blackpool', 'Blaenau Gwent', 'Bolsover', 'Bolton', 'Boston', 'Bournemouth, Christchurch and Poole', 'Bracknell Forest', 'Bradford', 'Braintree', 'Breckland', 'Brent', 'Brentwood', 'Bridgend', 'Brighton and Hove', 'Bristol, City of', 'Broadland', 'Bromley', 'Bromsgrove', 'Broxbourne', 'Broxtowe', 'Buckinghamshire', 'Burnley', 'Bury', 'Caerphilly', 'Calderdale', 'Cambridge', 'Camden', 'Cannock Chase', 'Canterbury', 'Cardiff', 'Carlisle', 'Carmarthenshire', 'Castle Point', 'Central Bedfordshire', 'Ceredigion', 'Charnwood', 'Chelmsford', 'Cheltenham', 'Cherwell', 'Cheshire East', 'Cheshire West and Chester', 'Chesterfield', 'Chichester', 'Chorley', 'City of London', 'Colchester', 'Conwy', 'Copeland', 'Cornwall', 'Cotswold', 'County Durham', 'Coventry', 'Craven', 'Crawley', 'Croydon', 'Dacorum', 'Darlington', 'Dartford', 'Denbighshire', 'Derby', 'Derbyshire Dales', 'Doncaster', 'Dorset', 'Dover', 'Dudley', 'Ealing', 'East Cambridgeshire', 'East Devon', 'East Hampshire', 'East Hertfordshire', 'East Lindsey', 'East Riding of Yorkshire', 'East Staffordshire', 'East Suffolk', 'Eastbourne', 'Eastleigh', 'Eden', 'Elmbridge', 'Enfield', 'Epping Forest', 'Epsom and Ewell', 'Erewash', 'Exeter', 'Fareham', 'Fenland', 'Flintshire', 'Folkestone and Hythe', 'Forest of Dean', 'Fylde', 'Gateshead', 'Gedling', 'Gloucester', 'Gosport', 'Gravesham', 'Great Yarmouth', 'Greenwich', 'Guildford', 'Gwynedd', 'Hackney', 'Halton', 'Hambleton', 'Hammersmith and Fulham', 'Harborough', 'Haringey', 'Harlow', 'Harrogate', 'Harrow', 'Hart', 'Hartlepool', 'Hastings', 'Havant', 'Havering', 'Herefordshire, County of', 'Hertsmere', 'High Peak', 'Hillingdon', 'Hinckley and Bosworth', 'Horsham', 'Hounslow', 'Huntingdonshire', 'Hyndburn', 'Ipswich', 'Isle of Anglesey', 'Isle of Wight', 'Isles of Scilly', 'Islington', 'Kensington and Chelsea', "King's Lynn and West Norfolk", 'Kingston upon Hull, City of', 'Kingston upon Thames', 'Kirklees', 'Knowsley', 'Lambeth', 'Lancaster', 'Leeds', 'Leicester', 'Lewes', 'Lewisham', 'Lichfield', 'Lincoln', 'Liverpool', 'Luton', 'Maidstone', 'Maldon', 'Malvern Hills', 'Manchester', 'Mansfield', 'Medway', 'Melton', 'Mendip', 'Merthyr Tydfil', 'Merton', 'Mid Devon', 'Mid Suffolk', 'Mid Sussex', 'Middlesbrough', 'Milton Keynes', 'Mole Valley', 'Monmouthshire', 'Neath Port Talbot', 'New Forest', 'Newark and Sherwood', 'Newcastle upon Tyne', 'Newcastle-under-Lyme', 'Newham', 'Newport', 'North Devon', 'North East Derbyshire', 'North East Lincolnshire', 'North Hertfordshire', 'North Kesteven', 'North Lincolnshire', 'North Norfolk', 'North Northamptonshire', 'North Somerset', 'North Tyneside', 'North Warwickshire', 'North West Leicestershire', 'Northumberland', 'Norwich', 'Nottingham', 'Nuneaton and Bedworth', 'Oadby and Wigston', 'Oldham', 'Oxford', 'Pembrokeshire', 'Pendle', 'Peterborough', 'Plymouth', 'Portsmouth', 'Powys', 'Preston', 'Reading', 'Redbridge', 'Redcar and Cleveland', 'Redditch', 'Reigate and Banstead', 'Rhondda Cynon Taf', 'Ribble Valley', 'Richmond upon Thames', 'Richmondshire', 'Rochdale', 'Rochford', 'Rossendale', 'Rother', 'Rotherham', 'Rugby', 'Runnymede', 'Rushcliffe', 'Rushmoor', 'Rutland', 'Ryedale', 'Salford', 'Sandwell', 'Scarborough', 'Sedgemoor', 'Sefton', 'Selby', 'Sevenoaks', 'Sheffield', 'Shropshire', 'Slough', 'Solihull', 'Somerset West and Taunton', 'South Cambridgeshire', 'South Derbyshire', 'South Gloucestershire', 'South Hams', 'South Holland', 'South Kesteven', 'South Lakeland', 'South Norfolk', 'South Oxfordshire', 'South Ribble', 'South Somerset', 'South Staffordshire', 'South Tyneside', 'Southampton', 'Southend-on-Sea', 'Southwark', 'Spelthorne', 'St Albans', 'St. Helens', 'Stafford', 'Staffordshire Moorlands', 'Stevenage', 'Stockport', 'Stockton-on-Tees', 'Stoke-on-Trent', 'Stratford-on-Avon', 'Stroud', 'Sunderland', 'Surrey Heath', 'Sutton', 'Swale', 'Swansea', 'Swindon', 'Tameside', 'Tamworth', 'Tandridge', 'Teignbridge', 'Telford and Wrekin', 'Tendring', 'Test Valley', 'Tewkesbury', 'Thanet', 'Three Rivers', 'Thurrock', 'Tonbridge and Malling', 'Torbay', 'Torfaen', 'Torridge', 'Tower Hamlets', 'Trafford', 'Tunbridge Wells', 'Uttlesford', 'Vale of Glamorgan', 'Vale of White Horse', 'Wakefield', 'Walsall', 'Waltham Forest', 'Wandsworth', 'Warrington', 'Warwick', 'Watford', 'Waverley', 'Wealden', 'Welwyn Hatfield', 'West Berkshire', 'West Devon', 'West Lancashire', 'West Lindsey', 'West Northamptonshire', 'West Oxfordshire', 'West Suffolk', 'Westminster', 'Wigan', 'Wiltshire', 'Winchester', 'Windsor and Maidenhead', 'Wirral', 'Woking', 'Wokingham', 'Wolverhampton', 'Worcester', 'Worthing', 'Wrexham', 'Wychavon', 'Wyre', 'Wyre Forest', 'York']
    return constit22

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def clean_files(path):
    critical_time = arrow.now().shift(hours=+1)
    print(critical_time)
    try:
        for item in Path(path).glob('*'):
            if item.is_file():
                itemTime = arrow.get(item.stat().st_mtime)
                if itemTime > critical_time:
                    os.remove(item)
    except:
        print("failed to clean path:", path)