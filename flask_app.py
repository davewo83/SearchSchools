from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for, request, make_response
from haversine import haversine

import requests, os

from settings import APP_STATIC

import json

app = Flask(__name__)

def get_saved_data():
    try:
        data = json.loads(request.cookies.get('postcode'))
    except TypeError:
        data = {}
    return data

def get_saved_mapdata():
    try:
        mapdata = json.loads(request.cookies.get('mapsdata'))
    except TypeError:
        mapdata = {}
    return mapdata

@app.route('/')
def index():
    data = get_saved_data()
    return render_template("index.html", saves=data)

@app.route('/save', methods=['POST'])
def save():
    response = make_response(redirect(url_for('schools')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('postcode', json.dumps(data))
    postcode = data['postcode']
    responsegm = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?address=" + postcode + "&key=AIzaSyBH1JmyXN748ThqJ5YyQp2PdogAW1DqqHA")
    data2 = responsegm.json()
    response.set_cookie('mapsdata', json.dumps(data2))
    return response

@app.route('/schools')
def schools():
    mapdata = get_saved_mapdata()
    address = mapdata['results'][0]['formatted_address']
    lat = float(mapdata['results'][0]['geometry']['location']['lat'])
    lng = float(mapdata['results'][0]['geometry']['location']['lng'])
    with open(os.path.join(APP_STATIC, "schools.json")) as json_file:
        json_data = json.load(json_file)
        print(json_data)
    for item in json_data:
        lat2 = item['Lat']
        lng2 = item['Lng']
        postcodelatlng = (lat,lng)
        schoollatlng = (lat2,lng2)
        dist=haversine(postcodelatlng,schoollatlng)
        item.update({"Dist":dist})
    json_data_sort = sorted(json_data, key=lambda distance: distance['Dist'])
    return render_template("schools.html", saves=get_saved_data(), data=json_data_sort, address=address)

@app.route('/details')
def details():
    mapdata = get_saved_mapdata()
    address=mapdata['results'][0]['formatted_address']
    lat=str(mapdata['results'][0]['geometry']['location']['lat'])
    lng=str(mapdata['results'][0]['geometry']['location']['lng'])
    responsepo = requests.get(
    "https://data.police.uk/api/crimes-street/all-crime?lat="+lat+"&lng="+lng)
    data2 = responsepo.json()
    i = 0
    vc = 0
    while i < (len(data2)):
        if (data2[i]['category'] == 'violent-crime'):
            vc += 1
        i += 1
    crimeno = len(data2)
    print(vc)
    if vc == 1:
        words = "was a violent crime."
    else:
        words = "were violent crimes."
    return render_template("", address=address, crimeno = crimeno, vc = vc, saves=get_saved_data(), words = words)



if __name__ == '__main__':
    app.run()
