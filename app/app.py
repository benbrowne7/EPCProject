
from flask import Flask, render_template, flash, redirect, url_for, request, session

from flask_navigation import Navigation
from config import Config


from maps import map1
import requests
import json
import os
from datetime import datetime, timedelta
import numpy as np
from numpy import interp
import pandas as pd

app = Flask(__name__)
nav = Navigation(app)
app.config.from_object(Config)



abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

endpoint = "https://epc.opendatacommunities.org/api/v1/domestic/search"
endpointcert = "https://epc.opendatacommunities.org/api/v1/domestic/certificate/"
endpointrec = "https://epc.opendatacommunities.org/api/v1/domestic/recommendations/"
auth = "Basic bm0yMDUyOUBicmlzdG9sLmFjLnVrOjY1MjE5ZjU0ODllM2E4YTU4MWYwMDA5MTAzYmVmOTMxM2U4Y2NhYzI="

headers = {}
headers["Accept"] = 'application/json'
headers["Authorization"] = auth

LAD_EPC_MEAN = 63.7
LAD_HPR_MEAN = 0.875

nav.Bar('top', [nav.Item('Individual', 'index'), nav.Item('Council', 'councilepc'), nav.Item('Reset', 'index')])


@app.route('/', methods=['GET', 'POST'])
def index():
        session.clear()
        abspath = os.path.abspath(__file__)
        sourcedir = os.path.dirname(abspath)
        if os.path.isfile(sourcedir + "/map1.html"):
            map1()
        rendermap1()
        return render_template('index.html')

@app.route('/councilepc', methods=['GET'])
def councilepc():
    session.pop('save', None)
    session.pop('house_list', None)
    session.pop('compare', None)
    if 'names' not in session:
        names = getconstitnames()
        session['names'] = names
    else:
        names = session['names']
    top = ['Tower Hamlets', 'Milton Keynes', 'City of London', 'Greenwich', 'Hackney']
    bottom = ['Isles of Scilly', 'Gwynedd', 'Ceredigion', 'Isle of Anglesey', 'Eden', 'Carmarthenshire', 'Powys']

    if 'save1' not in session:
        return render_template('councilepc.html', top=top, bottom=bottom, names=names)

    else:
        [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1] = session['save1']

        return render_template('councilepc.html', epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)

@app.route('/councilhpr', methods=['GET'])
def councilhpr():
    session.pop('save', None)
    session.pop('house_list', None)
    session.pop('compare', None)
    if 'names' not in session:
        names = getconstitnames()
        session['names'] = names
    else:
        names = session['names']
    top = ['Telford and Wrekin', 'Milton Keynes', 'Basingstoke and Deane', 'Eastleigh', 'Vale of White Horse']
    bottom = ['Kensington and Chelsea', 'Hammersmith and Fulham', 'Westminster', 'Camden', 'Haringey', 'Richmond upon Thames']

    if 'save1' not in session:
        return render_template('councilhpr.html', top=top, bottom=bottom, names=names)

    else:
        [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1] = session['save1']

        return render_template('councilhpr.html', epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)

@app.route('/ladsingle', methods=['GET','POST'])
def ladsingle():
    if 'names' not in session:
        names = getconstitnames()
        session['names'] = names
    else:
        names = session['names']
    url = request.referrer
    if "councilepc" in url:
        ret = "councilepc.html"
    else:
        ret = "councilhpr.html"
    names = session['names']

    constit_name = request.form['singlelad']
    ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    ons = ons2lad[ons2lad['LAD20NM'] == constit_name]['LAD20CD'].values[0]

    epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons)

    session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1]

    return render_template(ret, epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)

@app.route('/ladreq', methods=['POST'])
def ladrequest():
    if 'names' not in session:
        names = getconstitnames()
        session['names'] = names
    else:
        names = session['names']
    url = request.referrer
    if "councilepc" in url:
        ret = "councilepc.html"
    else:
        ret = "councilhpr.html"
    #check if ons code supplied has data
    abspath = os.path.abspath(__file__)
    sourcedir = os.path.dirname(abspath)
    checker = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)
    code_list = checker['ONS'].tolist()
    ons = request.form['ladreq']
    if ons not in code_list:
        valid = False
        return render_template(ret, valid=valid, names=names)
    else:
        epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons)

        session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1]

        return render_template(ret, epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)

@app.route('/epcdetails', methods=['POST'])
def epcdetails():

    [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag] = session['save']
    house_list = session['house_list']

    return render_template('index.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list)

@app.route('/compare', methods=['POST'])
def compare():
    [location1, ratings1, property1, features1, improvements1, e_date1, e_walls1, e_roof1, x, x1] = session['save']
    house_list = session['house_list']
    #get details to compare within postcode
    comparisions = session['compare']
    epc_rating = int(ratings1['current-int'])
    postcode = comparisions['postcode']
    postcode = ''.join(postcode.split())
    postcode = postcode.upper()
    url = endpoint + "?size=1000" + "&postcode={}".format(postcode)
    r = requests.get(url, headers=headers)
    data = r.json()
    rating_list = []
    hpr_list = []
    hpr = comparisions['hpr']

    #calculate postcode hpr values
    for house in data['rows']:
        x, ratings, x1, features = organizedata(house)
        rating_list.append(int(ratings['current-int']))
        hpr_list.append(heatpumpready(ratings, features)[0])
    average_epc = int(np.mean(rating_list))
    average_hpr = round(np.mean(hpr_list), 1)
    percentile_epc = np.percentile(rating_list, [10,20,30,40,50,60,70,80,90])
    percentile_hpr = np.percentile(hpr_list, [10,20,30,40,50,60,70,80,90])

    index_x, index_x1 = findpositioninpercentile(epc_rating, percentile_epc, hpr, percentile_hpr)
    tag1, tag2 = percentilecolours(index_x, index_x1)

    epc_string1 = "Your EPC rating [{}] is within the ".format(epc_rating)
    hpr_string1 = "Your HPR rating [{}] is within the ".format(hpr)
    epc_string2 = "{}th -> {}th percentile ".format(index_x*10, (index_x+1)*10)
    hpr_string2 = "{}th -> {}th percentile ".format(index_x1*10, (index_x1+1)*10)
    postcode_string = "for postcode {}".format(location1['postcode'])

    #find local authority info
    abspath = os.path.abspath(__file__)
    sourcedir = os.path.dirname(abspath)
    local_ons = location1['local']
    df = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    index = df.index[df['LAD20CD'] == local_ons].tolist()
    if index == []:
        local = local_ons
    else:
        local = df['LAD20NM'][index[0]]

    df = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)
    r = df.loc[df['ONS'] == local_ons]
    if r.empty:
        valid = False
        return render_template('comparesingle.html', location=location1, ratings=ratings1, property=property1, features=features1, improvements=improvements1, average_epc=average_epc, average_hpr=average_hpr, epc_string1=epc_string1, epc_string2=epc_string2, hpr_string1=hpr_string1, hpr_string2=hpr_string2, postcode_string=postcode_string, tag1=tag1, tag2=tag2, valid=valid)
    else:
        valid = True

    local_epc = r['EPC_MEAN'].values[0]
    local_hpr = r['HPR_MEAN'].values[0]
    samp = r['EPC_PERCENTILES'].values[0]
    samp1 = r['HPR_PERCENTILES'].values[0]

    samp = samp[1:len(samp)-1].split(',')
    samp1 = samp1[1:len(samp1)-1].split(',')
    percentile_local_epc = [int(float((x))) for x in samp]
    percentile_local_hpr = [float(x) for x in samp1]

    #for filename in os.listdir(sourcedir + "/data/hprs/"):
    #    if local in filename:
    #        f = sourcedir + "/data/hprs/" + filename
    #        break
    #df = pd.read_csv(f, low_memory=False)
    #epcs = df.iloc[:,0]
    #hprs = df.iloc[:,1]
    #local_epc = int(np.mean(epcs))
    #local_hpr = round(np.mean(hprs), 1)
    #percentile_local_epc = np.percentile(epcs, [10,20,30,40,50,60,70,80,90])
    #percentile_local_hpr = np.percentile(hprs, [10,20,30,40,50,60,70,80,90])

    index_y, index_y1 = findpositioninpercentile(epc_rating, percentile_local_epc, hpr, percentile_local_hpr)
    tag3, tag4 = percentilecolours(index_y, index_y1)

    epc_local1 = "Your EPC rating [{}] is within the ".format(epc_rating)
    hpr_local1 = "Your HPR rating [{}] is within the ".format(hpr)
    epc_local2 = "{}th -> {}th percentile ".format(index_y*10, (index_y+1)*10)
    hpr_local2 = "{}th -> {}th percentile ".format(index_y1*10, (index_y1+1)*10)
    local_string = "for local authority {}".format(local)


    return render_template('comparesingle.html', location=location1, ratings=ratings1, property=property1, features=features1, improvements=improvements1, average_epc=average_epc, average_hpr=average_hpr, epc_string1=epc_string1, epc_string2=epc_string2, hpr_string1=hpr_string1, hpr_string2=hpr_string2, postcode_string=postcode_string, tag1=tag1, tag2=tag2, local=local, local_epc=local_epc, local_hpr=local_hpr, epc_local1=epc_local1, hpr_local1=hpr_local1, epc_local2=epc_local2, hpr_local2=hpr_local2, local_string=local_string, tag3=tag3, tag4=tag4, house_list=house_list, valid=valid)

@app.route('/postcode', methods=['POST', 'GET'])
def postcodereq():
    if request.method == 'POST':
        session['keys'] = {}
        if len(request.form) == 1:
            postcode = request.form["postcode"]
            if (len(postcode) < 5) or (len(postcode) > 8):
                #invalid postcode
                valid = False
                return render_template('index.html', valid=valid)
            postcode = ''.join(postcode.split())
            postcode = postcode.upper()
            headers = {}
            headers["Accept"] = 'application/json'
            headers["Authorization"] = auth
            url = endpoint + "?size=100" + "&postcode={}".format(postcode)
            r = requests.get(url, headers=headers)
            if r == None:
                valid = False
                return render_template('index.html', valid=valid)
            data = r.json()
            for house in data['rows']:
                print(house['address'])
        if len(request.form) == 2:
            postcode = request.form["postcode"]
            if (len(postcode) < 5) or (len(postcode) > 8):
                valid = False
                return render_template('index.html', valid=valid)
            postcode = ''.join(postcode.split())
            postcode = postcode.upper()
            headers = {}
            headers["Accept"] = 'application/json'
            headers["Authorization"] = auth
            url = endpoint + "?size=100" + "&postcode={}".format(postcode)
            r = requests.get(url, headers=headers)
            if r == None:
                valid = False
                return render_template('index.html', valid=valid)
            data = r.json()
            house_list = []
            key_dict = {}
            for house in data['rows']:
                house_list.append(house['address'])
                key_dict[house['address']] = house['lmk-key']
            session['keys'] = key_dict
            session['house_list'] = house_list
            return render_template('addressselector.html', house_list=house_list)

    if request.method == 'GET':
         return render_template('index.html')
    return render_template('index.html')

@app.route('/singlerequest', methods=['POST', 'GET'])
def singlerequest():

    session.pop('save', None)
    session.pop('compare', None)
    house_list = session['house_list']

    #get certificate info
    if request.method == 'GET':
        return redirect(url_for('index'))
    address = request.form['singleaddress']
    key_dict = session['keys']
    key = key_dict[address]
    url = endpointcert + key
    r = requests.get(url, headers=headers)
    data = r.json()
    d = data['rows'][0]

    comparisons = {}
    comparisons['postcode'] = d['postcode']
    comparisons['rating'] = d['current-energy-efficiency']
    comparisons['type'] = d['property-type']
    location, ratings, property, features = organizedata(d)


    #get and clean up recommended improvements
    improvements = {}
    url = endpointrec + key
    g = requests.get(url, headers=headers)
    if g.status_code == 404:
        return render_template('index.html', location=location, ratings=ratings, property=property, features=features)
    data1 = g.json()
    for improvement in data1['rows']:
        if improvement['improvement-id-text'] == '':
            if improvement['improvement-summary-text'] == '':
                x = determineimprovement(improvement['improvement-descr-text'])
                improvements[x] = "estimated cost not available"
            else:
                improvements[improvement['improvement-summary-text']] = improvement['indicative-cost']
        else:
            improvements[improvement['improvement-id-text']] = improvement['indicative-cost']

    #determine boiler upgrade scheme eligibility
    current_date = datetime.today().strftime('%Y-%m-%d')
    cert_date = property['date']
    e_date = checkdates(cert_date, current_date)

    if features['walls-rate'] == ('Very Poor' or 'Poor'):
        e_walls = False
    else:
        e_walls = True
    if features['roof-rate'] == ('Very Poor' or 'Poor'):
        e_roof = False
    else:
        e_roof = True

    #calculate heat pump ready score
    hpr, tag = heatpumpready(ratings, features)

    comparisons['hpr'] = hpr
    session['compare'] = comparisons
    session['save'] = [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag]

    return render_template('index.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list)

@app.route('/map1', methods=['GET'])
def rendermap1():
    return render_template('maps/map1.html')

@app.route('/epcbylad', methods=['GET'])
def rendermap2():
    return render_template('maps/epcbylad.html')

@app.route('/hprbylad', methods=['GET'])
def rendermap3():
    return render_template('maps/hprbylad.html')




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

def singleladrequest(ons):
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
    epc_string1 = "Mean EPC for {} is [{}]".format(name, epc_mean)
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



if __name__ == '__main__':
      app.run(debug=True, host="0.0.0.0")




