
from flask import Flask, render_template, flash, redirect, url_for, request, session

from flask_navigation import Navigation
from config import Config


from maps import *
import requests
import json
import os
from datetime import datetime, timedelta
import numpy as np
from numpy import interp
import pandas as pd
from helper import *
from os.path import exists

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

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

nav.Bar('top', [nav.Item('Individual', 'individual'), nav.Item('LAD', 'councilepc'), nav.Item('Reset', 'index')])

@app.route('/')
def index():
    session.clear()
    if os.path.exists(sourcedir + "/templates/bigmap/constit_map.html"):
        os.remove(sourcedir + "/templates/bigmap/constit_map.html")
    return render_template("base.html")
    #return councilepc()

@app.route('/individual', methods=['GET', 'POST'])
def individual():
        session.pop('save', None)
        session.pop('house_list', None)
        session.pop('compare', None)
        abspath = os.path.abspath(__file__)
        sourcedir = os.path.dirname(abspath)
        rendermap1()
        return render_template('individual.html')

@app.route('/councilepc', methods=['GET','POST'])
def councilepc():
    session.pop('save', None)
    session.pop('house_list', None)
    session.pop('compare', None)
    names = getconstitnames()

    if 'save1' not in session:
        return render_template('councilepc.html', names=names)

    else:
        [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1] = session['save1']

        return render_template('councilepc.html', epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)


@app.route('/ladsingle', methods=['GET','POST'])
def ladsingle():
    names = getconstitnames()
    url = request.referrer
    if url == None:
        return render_template('councilepc.html', names=names)


    constit_name = request.form['singlelad']
    ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    try:
        ons = ons2lad[ons2lad['LAD20NM'] == constit_name]['LAD20CD'].values[0]
    except:
        print("not find ons")
        return render_template('councilepc.html', names=names, valid1=False)
    else:
        (w,h) = session['dimen']
        name, av_yoy, exp = graph(ons,w,h)
        session['name'] = name
        ladmap(ons,w,h)

        exp_str = "{}% of Certificates for {} have Expired".format(exp,ons)

        epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons, av_yoy)

        session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1, exp_str]
        session['ons'] = ons

        return render_template("councilepc.html", epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1, exp_str=exp_str)


@app.route('/ladreq', methods=['POST'])
def ladrequest():
    names = getconstitnames()
    url = request.referrer
    if url == None:
        return render_template('councilepc.html', names=names)
    #check if ons code supplied has data
    abspath = os.path.abspath(__file__)
    sourcedir = os.path.dirname(abspath)
    checker = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)
    code_list = checker['ONS'].tolist()
    ons = request.form['ladreq']
    if ons not in code_list:
        valid = False
        return render_template("councilepc.html", valid=valid, names=names)
    else:
        (w,h) = session['dimen']
        name, av_yoy, exp = graph(ons,w,h)
        session['name'] = name
        ladmap(ons,w,h)
        session['ons'] = ons

        exp_str = "{}% of Certificates for {} have Expired".format(exp,ons)

        epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons, av_yoy)

        session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1, exp_str]

        return render_template("councilepc.html", epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1, exp_str=exp_str)



@app.route('/epcdetails', methods=['POST'])
def epcdetails():

    [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag, conf] = session['save']
    house_list = session['house_list']

    return render_template('individual.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list)

@app.route('/compare', methods=['POST'])
def compare():
    [location1, ratings1, property1, features1, improvements1, e_date1, e_walls1, e_roof1, x, x1, conf] = session['save']
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
                valid = False
                print("g")
                return render_template('individual.html', valid=valid)
            postcode = ''.join(postcode.split())
            postcode = postcode.upper()
            headers = {}
            headers["Accept"] = 'application/json'
            headers["Authorization"] = auth
            url = endpoint + "?size=100" + "&postcode={}".format(postcode)
            r = requests.get(url, headers=headers)
            if r == None:
                valid = False
                return render_template('individual.html', valid=valid)
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
         return render_template('individual.html')
    return render_template('individual.html')

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
    wall = features['walls-rate']
    roof = features['roof-rate']

    if wall == 'Very Poor' or wall == 'Poor':
        e_walls = False
    else:
        e_walls = True
    if roof == 'Very Poor' or roof == 'Poor':
        e_roof = False
    else:
        e_roof = True

    #calculate confidence metric
    year = int(cert_date.split('-')[0])
    while True:
        if year >= 2018:
            conf = 0
            break
        if year >= 2013:
            conf = 1
            break
        else:
            conf = 2
            break

    #calculate heat pump ready score
    hpr, tag = heatpumpready(ratings, features)

    comparisons['hpr'] = hpr
    session['compare'] = comparisons
    session['save'] = [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag, conf]

    return render_template('individual.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list, conf=conf)

@app.route('/graphdimen', methods=['POST'])
def graphdimen():
    print("in graphdimen", flush=True)
    out = request.get_json(force=True)
    print(out)
    w = out['data1']
    h = out['data2']
    session['dimen'] = (w,h)
    print(session['dimen'])
    return 'h'

@app.route('/bigmap', methods=['GET'])
def rendermap1():
    w,h = session['dimen']
    bigmap(w,h)
    return render_template('bigmap/constit_map.html')

@app.route('/graphpane')
def rendermap5():
    file = session['name']
    return render_template('graphs/' + file)

@app.route('/ladmapleft')
def rendermap6():
    ons = session['ons']
    return render_template('ladmaps/' + ons + '_map.html')





if __name__ == '__main__':
      app.run(debug=True, host="0.0.0.0")




