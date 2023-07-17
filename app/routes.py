
from flask import Flask, render_template, flash, redirect, url_for, request, session

from flask_navigation import Navigation
from config import Config
from flask import current_app as app


from .maps import *
import requests
import json
import os
from datetime import datetime, timedelta
import numpy as np
from numpy import interp
import pandas as pd
from .helper import *
from os.path import exists


#app = Flask(__name__)
#nav = Navigation(app)
#app.config.from_object(Config)




abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

endpoint = "https://epc.opendatacommunities.org/api/v1/domestic/search"
endpointcert = "https://epc.opendatacommunities.org/api/v1/domestic/certificate/"
endpointrec = "https://epc.opendatacommunities.org/api/v1/domestic/recommendations/"
epc = "https://find-energy-certificate.service.gov.uk/find-a-certificate/search-by-postcode?postcode="
auth = "Basic bm0yMDUyOUBicmlzdG9sLmFjLnVrOjY1MjE5ZjU0ODllM2E4YTU4MWYwMDA5MTAzYmVmOTMxM2U4Y2NhYzI="

headers = {}
headers["Accept"] = 'application/json'
headers["Authorization"] = auth

LAD_EPC_MEAN = 63.7
LAD_HPR_MEAN = 0.875

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)



@app.route('/')
def index():
    session.clear()
    return render_template("base.html")

@app.route('/individual', methods=['GET', 'POST'])
def individual():
        session.pop('save', None)
        session.pop('house_list', None)
        session.pop('compare', None)
        session.pop('save1', None)
        session.pop('grid-stats', None)
        session.pop('keys', None)
        abspath = os.path.abspath(__file__)
        sourcedir = os.path.dirname(abspath)
        rendermap1()
        return render_template('individual.html')

@app.route('/lad', methods=['GET','POST'])
def lad():
    session.pop('save', None)
    session.pop('house_list', None)
    session.pop('compare', None)
    session.pop('grid-stats', None)
    session.pop('keys', None)
    names = getconstitnames()

    if 'save1' not in session:
        return render_template('lad.html', names=names)

    else:
        [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1, exp_str] = session['save1']
        try:
            names.remove(name)
        except:
            print("name not in list")
        else:
            names.append(name)

        return render_template('lad.html', epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1)

@app.route('/grid', methods=['GET','POST'])
def grid():
    (w,h) = session['dimen']
    session.clear()
    session['dimen'] = (w,h)
    capacity, headroom, utilization = biggrid(w,h)
    constit22 = getconstitnames()
    session['grid-stats'] = (capacity, headroom, utilization)
    return render_template('grid.html', capacity=capacity, headroom=headroom, utilization=utilization, constit22=constit22)

@app.route('/gridsingle', methods=['POST', 'GET'])
def gridsingle():
    try:
        constit_name = request.form['singlegrid']
    except:
        constit22 = getconstitnames()
        (capacity, headroom, utilization) = session['grid-stats']
        return render_template('grid.html', capacity=capacity, headroom=headroom, utilization=utilization, constit22=constit22)
    
    if constit_name == "na":
        (w,h) = session['dimen']
        capacity, headroom, utilization = biggrid(w,h)
        session['grid-stats'] = (capacity, headroom, utilization)
        return render_template('grid.html', capacity=capacity, headroom=headroom, utilization=utilization, constit22=constit22)


    (w,h) = session['dimen']
    constit22 = getconstitnames()
    constit22.remove(constit_name)
    constit22.append(constit_name)
    try:
        (capacity, headroom, utilization) = session['grid-stats']
    except:
        capacity, headroom, utilization = biggrid(5,5,True)
        session['grid-stats'] = (capacity, headroom, utilization)
    

    ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv")
    row = ons2lad.loc[ons2lad['LAD20NM'] == constit_name]
    try:
        ons = row['LAD20CD'].values[0]
    except:
        valid = False
        return render_template('grid.html', capacity=capacity, headroom=headroom, utilization=utilization, constit22=constit22, valid=valid, constit_name=constit_name)
    
    session['ons'] = ons
    
    valid_substations = biggridsingle(w,h, constit_name, ons)

    num_epcs_df = pd.read_csv(sourcedir + "/data/number_epcs.csv")
    row = num_epcs_df.loc[num_epcs_df['ONS'] == ons]
    num_epcs = int(row['NUM'].values[0])


    if not valid_substations:
        valid = False
        return render_template('grid.html', capacity=capacity, headroom=headroom, utilization=utilization, constit22=constit22, valid=valid, constit_name=constit_name)
    else:
        valid = True
        num_substations, capacity_single, headroom_single, utilization_single, dno = extractsubstationinfo(valid_substations)
        max_support = int((headroom_single-(capacity_single*0.1)) / 0.0017)
        perc_homes = round((max_support / num_epcs)*100,1)
        ten_perc = int(int(num_epcs*0.1) * 0.0017)

        if utilization_single == 0 and capacity_single == 0:
            utilization_single = 'Data Not Available'
            capacity_single = 'Data Not Available'
            northwest = True
            max_support = int(headroom_single*0.9 / 0.0017)
            perc_homes = round((max_support / num_epcs)*100,1)
        else:
            northwest = False

        return render_template('grid.html', constit22=constit22, valid=valid, constit_name=constit_name, capacity=capacity, headroom=headroom, utilization=utilization, capacity_single=capacity_single, headroom_single=headroom_single, utilization_single=utilization_single, num_substations=num_substations, num_epcs=num_epcs, max_support=max_support, perc_homes=perc_homes, dno=dno, northwest=northwest, ten_perc=ten_perc)
    
    

@app.route('/ladsingle', methods=['GET','POST'])
def ladsingle():
    names = getconstitnames()
    print(names)
    url = request.referrer
    if url == None:
        return render_template('lad.html', names=names)

    constit_name = request.form['singlelad']
    ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    try:
        ons = ons2lad[ons2lad['LAD20NM'] == constit_name]['LAD20CD'].values[0]
    except:
        print("not find ons")
        return render_template('lad.html', names=names, valid1=False)
    else:
        (w,h) = session['dimen']
        name, av_yoy, exp = graph(ons,w,h)
        names.remove(constit_name)
        names.append(constit_name)
        ladmap(ons,w,h)

        exp_str = "{}% of Certificates for {} have Expired".format(exp,ons)

        epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons, av_yoy)

        session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1, exp_str]
        session['ons'] = ons

        return render_template("lad.html", epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1, exp_str=exp_str, constit_name=constit_name)


@app.route('/ladreq', methods=['POST'])
def ladrequest():
    names = getconstitnames()
    url = request.referrer
    if url == None:
        return render_template('lad.html', names=names)
    #check if ons code supplied has data
    abspath = os.path.abspath(__file__)
    sourcedir = os.path.dirname(abspath)
    checker = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)
    code_list = checker['ONS'].tolist()
    ons = request.form['ladreq']
    if ons not in code_list:
        valid = False
        return render_template("lad.html", valid=valid, names=names)
    else:
        (w,h) = session['dimen']
        name, av_yoy, exp = graph(ons,w,h)
        session['name'] = name

        ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
        constit_name = ons2lad[ons2lad['LAD20CD'] == ons]['LAD20NM'].values[0]
        names.remove(constit_name)
        names.append(constit_name)
        
        ladmap(ons,w,h)
        session['ons'] = ons

        exp_str = "{}% of Certificates for {} have Expired".format(exp,ons)

        epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, n_over1 = singleladrequest(ons, av_yoy)

        session['save1'] = [epc_string1, hpr_string1, epc_string2, hpr_string2, tag1, tag2, proportion_string, name, ons, n_over1, exp_str]

        return render_template("lad.html", epc_string1=epc_string1, hpr_string1=hpr_string1, epc_string2=epc_string2, hpr_string2=hpr_string2, tag1=tag1, tag2=tag2, proportion_string=proportion_string, name=name, names=names, ons=ons, LAD_EPC_MEAN=LAD_EPC_MEAN, LAD_HPR_MEAN=LAD_HPR_MEAN, n_over1=n_over1, exp_str=exp_str)


@app.route('/epcdetails', methods=['POST'])
def epcdetails():

    [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag, conf, improve_str, epc_link] = session['save']
    house_list = session['house_list']

    return render_template('individual.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list, conf=conf, improve_str=improve_str, epc_link=epc_link)

@app.route('/compare', methods=['POST'])
def compare():
    [location1, ratings1, property1, features1, improvements1, e_date1, e_walls1, e_roof1, x, x1, conf, improve_str, epc_link] = session['save']
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
        return render_template('comparesingle.html', location=location1, ratings=ratings1, property=property1, features=features1, improvements=improvements1, average_epc=average_epc, average_hpr=average_hpr, epc_string1=epc_string1, epc_string2=epc_string2, hpr_string1=hpr_string1, hpr_string2=hpr_string2, postcode_string=postcode_string, tag1=tag1, tag2=tag2, valid=valid, improve_str=improve_str)
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


    return render_template('comparesingle.html', location=location1, ratings=ratings1, property=property1, features=features1, improvements=improvements1, average_epc=average_epc, average_hpr=average_hpr, epc_string1=epc_string1, epc_string2=epc_string2, hpr_string1=hpr_string1, hpr_string2=hpr_string2, postcode_string=postcode_string, tag1=tag1, tag2=tag2, local=local, local_epc=local_epc, local_hpr=local_hpr, epc_local1=epc_local1, hpr_local1=hpr_local1, epc_local2=epc_local2, hpr_local2=hpr_local2, local_string=local_string, tag3=tag3, tag4=tag4, house_list=house_list, valid=valid, improve_str=improve_str)

@app.route('/postcode', methods=['POST', 'GET'])
def postcodereq():
    if request.method == 'POST':
        session['keys'] = {}

        if len(request.form) == 1:
            postcode = request.form["postcode"]
            if (len(postcode) < 5) or (len(postcode) > 8):
                valid = False
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

            house_list.sort(key=natural_keys)
            session['house_list'] = house_list
            return render_template('addressselector.html', house_list=house_list)

    if request.method == 'GET':
         return render_template('individual.html')
    return render_template('individual.html')

@app.route('/singlerequest', methods=['POST', 'GET'])
def singlerequest():
    #session.pop('save', None)
    #session.pop('compare', None)
    try:
        house_list = session['house_list']
    except:
        return render_template('individual.html')

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
    ons = d['local-authority']


    comparisons = {}
    comparisons['postcode'] = d['postcode']
    comparisons['rating'] = d['current-energy-efficiency']
    comparisons['type'] = d['property-type']
    location, ratings, property, features = organizedata(d)

    posty = d['postcode']
    posty = ''.join(posty.split())
    epc_link = epc + posty


    #get and clean up recommended improvements
    improvements = {}
    url = endpointrec + key
    g = requests.get(url, headers=headers)
    if g.status_code == 404:
        return render_template('individual.html', location=location, ratings=ratings, property=property, features=features, epc_link=epc_link)
    data1 = g.json()
    for improvement in data1['rows']:
        if len(improvements) == 4:
            break
        if improvement['improvement-id-text'] == '':
            if improvement['improvement-summary-text'] == '':
                x = determineimprovement(improvement['improvement-descr-text'])
                improvements[x] = "estimated cost not available"
            else:
                improvements[improvement['improvement-summary-text']] = improvement['indicative-cost']
        else:
            improvements[improvement['improvement-id-text']] = improvement['indicative-cost']

    improve_str = "{} / {} displayed".format(len(improvements), len(data1['rows']))



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
    today = datetime.today()
    current_year = int(today.year)
    while True:
        if year >= current_year-5:
            conf = 0
            break
        if year >= current_year-10:
            conf = 1
            break
        else:
            conf = 2
            break

    #calculate heat pump ready score
    hpr, tag = heatpumpready(ratings, features)

    comparisons['hpr'] = hpr
    session['compare'] = comparisons
    session['save'] = [location, ratings, property, features, improvements, e_date, e_walls, e_roof, hpr, tag, conf, improve_str, epc_link]

    df = pd.read_csv(sourcedir + "/data/ONS2LAD.csv", low_memory=False)
    index = df.index[df['LAD20CD'] == ons].tolist()
    if index == []:
        local = "na"
    else:
        local = df['LAD20NM'][index[0]]
        
    return render_template('individual.html', location=location, ratings=ratings, property=property, features=features, improvements=improvements, e_date=e_date, e_walls=e_walls, e_roof=e_roof, hpr=hpr, tag=tag, house_list=house_list, conf=conf, improve_str=improve_str, epc_link=epc_link, local=local)

@app.route('/ladadoption', methods=['POST', 'GET'])
def ladadoption():
    try:
        ons = session['ons']
    except:
        valid = False
        return render_template("lad.html", valid=valid)
    
    names = getconstitnames()
    (w,h) = session['dimen']
    graphadoption(ons,w,h)

    ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv")
    name = ons2lad.loc[ons2lad['LAD20CD'] == ons].values[0]
    constit_name = name[1]

    av_rate = 28.8
    rate_percentile = [12.59, 16.24, 18.97, 20.66, 23.1, 26.22, 30.6,  38.46, 51.34]
    av_density = 8.3
    density_percentile = [0.38, 0.778, 1.304, 2.346, 3.995, 6.552, 9.79, 15.1, 23.895]

    heatpump = pd.read_csv(sourcedir + "/data/heatpump-cum.csv", low_memory=False)
    population = pd.read_csv(sourcedir + "/data/population.csv", engine='python')

    try:
        cuml_data = heatpump.loc[heatpump['ONS'] == ons].values[0]
        pop_data = population.loc[population['ONS'] == ons].values[0]
    except:
        valid = False
    else:
        valid = True
        sum_val = sum(cuml_data[2:])
        pop_val = int(pop_data[2].replace(",", ""))
        rates = cuml_data[13:]
        lad_rate = (((rates[2] - rates[1]) / rates[1]) + ((rates[1] - rates[0]) / rates[0])) * 0.5
        lad_rate = round(lad_rate * 100,1)
        lad_density = round(sum_val / pop_val * 1000, 2)
        
    index0, index1 = findpositioninpercentile(lad_rate, rate_percentile, lad_density, density_percentile)
    tag0, tag1 = percentilecolours(index0, index1)

    av_rate_string = "Average Yearly % Increase in Heat Pumps (RHI Scheme): {}%".format(av_rate)
    av_density_string = "Average Number of Installed Heat Pumps per 1000 People (RHI Scheme): {}".format(av_density)
    lad_rate_string = "Average Yearly % Increase in Heat Pumps (RHI Scheme) for {}: [{}%]".format(name, lad_rate)
    lad_density_string = "Number of Installed Heat Pumps per 1000 People (RHI Scheme) for {}: [{}]".format(name, lad_density)

    rate_percentile_string = "{} is within the {}th -> {}th percentile for Local Authority Districts (av. annual % Increase)".format(name, index0*10, (index0+1)*10)
    density_percentile_string = "{} is within the {}th -> {}th percentile for Local Authority Districts (Heat Pumps per 1000)".format(name, index1*10, (index1+1)*10)

    return render_template("ladadoption.html", valid=valid, av_rate_string=av_rate_string, av_density_string=av_density_string, lad_rate_string=lad_rate_string, lad_density_string=lad_density_string, rate_percentile_string=rate_percentile_string, density_percentile_string=density_percentile_string, constit_name=constit_name, ons=ons, tag0=tag0, tag1=tag1, names=names)

@app.route('/docs', methods=['GET'])
def docs():
    return render_template("docs.html")





@app.route('/graphdimen', methods=['POST'])
def graphdimen():
    out = request.get_json(force=True)
    w = out['data1']
    h = out['data2']
    session['dimen'] = (w,h)
    print(session['dimen'])
    return render_template('lad.html')

@app.route('/bigmap', methods=['GET'])
def rendermap1():
    try:
        w,h = session['dimen']
    except:
        return True
    else:
        name = "constit_map_" + str(w) + "x" + str(h) + ".html"
        bigmap(w,h)
        return render_template('bigmap/' + name)

@app.route('/adoptionmap')
def rendermap2():
    try:
        w,h = session['dimen']
    except:
        return True
    else:
        adoptionmap(w,h)
        name = "adoption_map_" + str(w) + "x" + str(h) + ".html"
        return render_template('bigmap/' + name)

@app.route('/graphpane')
def rendermap5():
    ons = session['ons']
    w,h = session['dimen']
    name = ons + "_graph_" + str(w) + "x" + str(h) + ".html"
    return render_template('graphs/' + name)
@app.route('/graphpaneadoption')
def rendermap6():
    ons = session['ons']
    w,h = session['dimen']
    name = ons + "_graph_" + str(w) + "x" + str(h) + ".html"
    return render_template('graphsadoption/' + name)

@app.route('/ladmapleft')
def rendermap7():
    ons = session['ons']
    w, h = session['dimen']
    name = ons + "_" + str(w) + "x" + str(h) +  ".html"
    return render_template('ladmaps/' + name)

@app.route('/biggrid')
def rendermap8():
    w, h = session['dimen']
    name = "biggrid_" + str(w) + "x" + str(h) + ".html"
    return render_template('biggrid/' + name)

@app.route('/biggridsingle')
def rendermap9():
    ons = session['ons']
    w, h = session['dimen']
    name = ons + "_grid_" + str(w) + "x" + str(h) + ".html"
    return render_template('biggrid/' + name)






if __name__ == '__main__':
      app.run(debug=True, host="0.0.0.0")




