import folium
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import json
import re
import pandas as pd
import subprocess 
import glob
from shlex import quote
from joblib import Parallel, delayed
import math

import plotly.graph_objects as go

from geopy.geocoders import Nominatim
import random


geolocator = Nominatim(user_agent="mapgif"+str(random.randint(0,10000000)))

def get_address(Latitude, Longitude):
    location = geolocator.reverse(Latitude+","+Longitude)
    l=location.raw['address']
    addrs=[]
    if l.get('county'):
        addrs.append(l['county'])
    if l.get('city'):
        addrs.append(l['city'])
    elif l.get('state_district'):
        addrs.append(l['state_district'])

    if (len(addrs)==0):
        final=Latitude+","+Longitude
    else:
        final=", ".join(addrs)
    return final

def speedgauge(s,fname):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = s,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Speed"},
        gauge = {'axis': {'range': [None, 300]},
                'shape': "angular",
                'bar': {'color': "silver","thickness": 0.5},
                    'steps' : [
                        {'range': [0, 100], 'color': "mintcream"},
                        {'range': [100, 200], 'color': "orange"},
                        {'range': [200, 300], 'color': "orangered"}
                    ]}))
    fig.write_image(fname)


def dms2dd(l):
    r=re.search('(.*) deg (.*)\' (.*)" (.*)',l,re.IGNORECASE)
    deg=r.group(1)
    minutes=r.group(2)
    seconds=r.group(3)
    direction=r.group(4)
    return (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * (-1 if direction in ['W', 'S'] else 1)

def exif2df(xx):
    xy={'frame':[],'track':[],'speed':[],'lat':[],'long':[]}

    for k in xx.keys():
        if 'Doc' in k:
            xy['frame'].append(int(re.search("Doc([0-9]+)",k,re.IGNORECASE).group(1)))
            xy['track'].append(xx[k]['GPSTrack'])
            xy['speed'].append(xx[k]['GPSSpeed'])
            xy['lat'].append(dms2dd(xx[k]['GPSLatitude']))
            xy['long'].append(dms2dd(xx[k]['GPSLongitude']))
    df=pd.DataFrame(xy)
    return df.sort_values(by=["frame"])

def getexif(fname):
    output = subprocess.check_output(["exiftool","-j","-g3","-ee3",fname])
    xx=json.loads(output)[0]
    return xx


def generate_map_vid(fname,width=480, height=270, zoom_start=18, num_samp=10):
    xx=getexif(fname)
    df=exif2df(xx)
    lats=df['lat'].to_list()
    samps=max(1,math.floor(len(lats)/num_samp))
    lats=lats[0:-1:samps]
    longs=df['long'].to_list()
    longs=longs[0:-1:samps]

    N=math.ceil(math.log10(len(lats)))

    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    def map2png(i, lat, long, text_str):
        mymap = folium.Map(width=width,height=height,location=[lat,long],zoom_start=zoom_start, zoom_control=False)
        iframe='<div style="font-size: 16pt">{text}</div>'.format(text=text_str)
        popup=folium.Popup(iframe,show=True,max_width='250%')
        icon=folium.Icon(icon="motorcycle", prefix="fa",color="blue")
        folium.Marker([lat, long],popup=popup,icon=icon).add_to(mymap)
        img_data = mymap._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img.save(fname+"_gps_"+str(i).zfill(N)+".PNG")

    addrs=[get_address(str(lat),str(long)) for (lat,long) in zip(lats,longs)]
    _=Parallel(n_jobs=-1)(delayed(map2png)(i, lat, long, addr) for i, (lat, long, addr) in enumerate(zip(lats, longs, addrs)))

    _=subprocess.check_output(["convert","-delay","420","-loop","0",fname+"_gps_*.PNG",fname+"_gps.mp4"])
    files = glob.glob(fname+"_gps_*.PNG")
    args = ["rm "+quote(f) for f in files]
    for a in args:
        subprocess.Popen(a, shell=True)

    speeds=df['speed'].to_list()
    N=math.ceil(math.log10(len(speeds)))
    _=Parallel(n_jobs=-1)(delayed(speedgauge)(s, fname+"_speed_"+str(i).zfill(N)+".PNG") for i, s in enumerate(speeds))
    
    _=subprocess.check_output(["convert","-delay","17","-loop","0",fname+"_speed_*.PNG",fname+"_speed.mp4"])
    files = glob.glob(fname+"_speed_*.PNG")
    args = ["rm "+quote(f) for f in files]
    for a in args:
        subprocess.Popen(a, shell=True)

    driver.quit()
    return True

