from flask import render_template, flash, redirect, url_for, request, session
from app import app
from app.maps import map1
import requests
import json

endpoint = "https://epc.opendatacommunities.org/api/v1/domestic/search"
endpointcert = "https://epc.opendatacommunities.org/api/v1/domestic/certificate/"
auth = "Basic bm0yMDUyOUBicmlzdG9sLmFjLnVrOjY1MjE5ZjU0ODllM2E4YTU4MWYwMDA5MTAzYmVmOTMxM2U4Y2NhYzI="

headers = {}
headers["Accept"] = 'application/json'
headers["Authorization"] = auth


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
            #print(data)
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
        
        
@app.route('/singlerequest', methods=['POST'])  
def singlerequest():
    address = request.form['singleaddress']
    key_dict = session['keys']
    key = key_dict[address]
    url = endpointcert + key
    r = requests.get(url, headers=headers)
    data = r.json()
    print(data)
    return redirect(request.referrer)

    
@app.route('/map1', methods=['GET'])
def map1():
    return render_template('map1.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    title = 'Provision'
    form = TestForm()
    if form.validate_on_submit():
        
        # Capturing form input
        name = form.name.data
        surname = form.surname.data
        gender = form.gender.data
        sport = form.sport.data

        flash(f"Name: {name} {surname}, Gender: {gender}, Sport: {sport}", 'success')
        return redirect(url_for('form'))

    return render_template('form.html', title=title, form=form)
