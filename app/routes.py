from flask import render_template, flash, redirect, url_for, request, session

from app import app
from app import nav
from app.maps import map1
import requests
import json

endpoint = "https://epc.opendatacommunities.org/api/v1/domestic/search"
endpointcert = "https://epc.opendatacommunities.org/api/v1/domestic/certificate/"
auth = "Basic bm0yMDUyOUBicmlzdG9sLmFjLnVrOjY1MjE5ZjU0ODllM2E4YTU4MWYwMDA5MTAzYmVmOTMxM2U4Y2NhYzI="

headers = {}
headers["Accept"] = 'application/json'
headers["Authorization"] = auth

nav.Bar('top', [nav.Item('Home', 'index')])


@app.route('/', methods=['GET', 'POST'])
def index():
        map1()
        return render_template('index.html')

@app.route('/postcode', methods=['POST', 'GET'])
def postcodereq():
    if request.method == 'POST':
        session['keys'] = {}
        if len(request.form) == 1:
            postcode = request.form["postcode"]
            if (len(postcode) < 5) or (len(postcode) > 7):
                #invalid postcode
                return render_template('index.html')
            postcode = ''.join(postcode.split())
            postcode = postcode.upper()
            url = endpoint + "?size=100" + "&postcode={}".format(postcode)
            r = requests.get(url, headers=headers)
            data = r.json()
            for house in data['rows']:
                print(house['address'])
        if len(request.form) == 2:
            postcode = request.form["postcode"]
            if (len(postcode) < 5) or (len(postcode) > 7):
                #invalid postcode
                return render_template('index.html')
            postcode = ''.join(postcode.split())
            postcode = postcode.upper()
            headers = {}
            headers["Accept"] = 'application/json'
            headers["Authorization"] = auth
            url = endpoint + "?size=100" + "&postcode={}".format(postcode)
            r = requests.get(url, headers=headers)
            data = r.json()
            house_list = []
            key_dict = {}
            for house in data['rows']:
                house_list.append(house['address'])
                key_dict[house['address']] = house['lmk-key']
            session['keys'] = key_dict
            return render_template('addressselector.html', house_list=house_list)
             
    if request.method == 'GET':
         return render_template('index.html')
    return render_template('index.html')
        
        
@app.route('/singlerequest', methods=['POST', 'GET'])  
def singlerequest():
    if request.method == 'GET':
        return redirect(url_for('index'))
    address = request.form['singleaddress']
    key_dict = session['keys']
    key = key_dict[address]
    url = endpointcert + key
    r = requests.get(url, headers=headers)
    data = r.json()
    data = data['rows'][0]
    location, ratings, property, features = organizedata(data)
    return render_template('index.html', location=location, ratings=ratings, property=property, features=features)

    
@app.route('/map1', methods=['GET'])
def map1():
    return render_template('map1.html')


def organizedata(data):
    print(type(data))
    location = {}
    ratings = {}
    property = {}
    features = {}
    location['address1'] = data['address1']
    location['postcode'] = data['postcode']
    location['county'] = data['county']
    ratings['current'] = data['current-energy-rating']
    ratings['current-int'] = data['current-energy-efficiency']
    ratings['potential'] = data['potential-energy-rating']
    property['type'] = data['property-type']
    property['form'] = data['built-form']
    property['tenure'] = data['tenure']
    features['multi-glaze'] = data['multi-glaze-proportion']
    features['windows'] = data['windows-description']
    features['floors'] = data['floor-description']
    features['hot-water'] = data['hotwater-description']
    features['walls'] = data['walls-description']
    features['roof'] = data['roof-description']
    features['mainheat'] = data['mainheat-description']
    features['mainfuel'] = data['main-fuel']
    return location, ratings, property, features



