import json
import os
import sys
import time
import descartes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, Polygon
from numpy.random import choice
from geopy.geocoders import GoogleV3
from sklearn.cluster import SpectralClustering

api_file = open('API', 'r')
geolocator = GoogleV3(api_key=api_file.readline())
colors = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'cyan', 'black', 'brown', 'olive']

def add_lat_lon(voter):
    # TODO: Handle errors returned by google api
    address = voter["residence_street_number"] + " "
    if voter["pre_direction"]:
        address += voter["pre_direction"] + " "
    address += voter["street_name"] + " " + voter["street_type"] + ", "
    address += voter["city"] + ", " + voter["state"] + " " + voter["zip"] + ", USA"

    location = geolocator.geocode(address)

    if location == None:
        return False

    voter["complete_address"] = address
    voter["latitude"] = location.latitude
    voter["longitude"] = location.longitude
    return True

def lst_format(line):
    voter = {
            "first_name": line[35:55].strip(),
            "middle_name": line[55:75].strip(),
            "last_name": line[0:35].strip(),
            "residence_street_number": line[92:99].strip(),
            "pre_direction": line[103:105].strip(),
            "street_name": line[105:135].strip(),
            "street_type": line[135:141].strip(),
            "suffix direction": line[141:143].strip(),
            "residence_extension": line[143:156].strip(),
            "city": line[156:191].strip(),
            "state": line[191:193].strip(),
            "zip": line[193:198].strip(),
            "voterid": line[452:452+12].strip(),
            "state_house": line[479:484].strip(),
            "state_senate": line[484:489].strip(),
            "us_congress": line[489:494].strip(),
            "cluster": None,
            "complete_address": None,
            "latitude": None,
            "longitude": None,
        }
    return voter

def main():
    SAVE = False
    LOAD = False
    SAMPLE_SIZE = 25000
    CLUSTERS = 14

    if len(sys.argv) > 2: 
        print("Error: Too many arguments")

    if len(sys.argv) == 2 and sys.argv[1] == "--save": 
        SAVE = True

    if len(sys.argv) == 2 and sys.argv[1] == "--load": 
        LOAD = True

    processed_subset = []

    if not LOAD:
        if not os.path.isfile("./entire_state_v.lst"):
            print("Downloading voter data...")
            os.system("wget http://69.64.83.144/~mi/download/20170512/FOIA_Voters.zip")
            os.system("unzip FOIA_Voters.zip")
        else:
            print("Using existing voter data...")

        # Choose random subset of data
        print("Selecting random subset of voters...")
        in_file = "entire_state_v.lst"
        voter_lst = open(in_file, 'r')
        data = voter_lst.readlines()
        voter_lst.close()
        subset = choice(data, SAMPLE_SIZE, replace=False)

        processed_subset_json = None
        
        if SAVE:
            processed_subset_json = open("processed_subset.json", 'w+')

        print("Adding Google geocoding information...")
        for line in subset:
            voter = lst_format(line)
            if add_lat_lon(voter):
                processed_subset.append(voter)
            time.sleep(1/3000)

        if SAVE:
            print("Saving processed subset...")
            processed_subset_json.write(json.dumps(processed_subset))
            processed_subset_json.close()
        
    else:
        print("Loading processed subset...")
        processed_subset_json = open("processed_subset.json",)
        processed_subset = json.load(processed_subset_json)
        processed_subset_json.close()

    print("Clustering processed subset...")
    format_lat_lon = np.array([[voter["latitude"], voter["longitude"]] for voter in processed_subset])
    clustering = SpectralClustering(n_clusters=CLUSTERS).fit(format_lat_lon)

    for i in range(SAMPLE_SIZE):
        processed_subset[i]["cluster"] = int(clustering.labels_[i])

    print("Writing out results...")
    output_json = open("output.json", 'w+')
    output_json.write(json.dumps(processed_subset))
    output_json.close()
    
    print("Visualizing results...")
    df = pd.DataFrame(processed_subset)
    crs = {'init': 'epsg:4326'}
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    street_map = gpd.read_file('./michigan_administrative/michigan_administrative.shp')
    fig, ax = plt.subplots(figsize = (15, 15))
    out = street_map.plot(ax = ax, alpha=0.4, color='grey')
    for i in range(CLUSTERS):
        geo_df[geo_df['cluster'] == i].plot(ax=ax, markersize=20, color=colors[i%len(colors)], marker='o')

    fig = out.get_figure()  
    fig.savefig("map.png") 
    print("Done") 

if __name__ == "__main__":
    main()