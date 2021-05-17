import json
import os
import sys
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

def add_lat_lon(voter):
    address = voter["residence_street_number"] + " "
    if voter["pre_direction"]:
        address += voter["pre_direction"] + " "
    address += voter["street_name"] + " " + voter["street_type"] + ", "
    address += voter["city"] + ", " + voter["state"] + " " + voter["zip"] + ", USA"

    # location = geolocator.geocode(address)

    voter["complete_address"] = address
    # voter["latitude"] = location.latitude
    # voter["longitude"] = location.longitude

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
    SAMPLE_SIZE = 25
    CLUSTERS = 3

    if len(sys.argv) > 2: 
        print("Error: Too many arguments")

    if len(sys.argv) == 2 and sys.argv[1] == "--save": 
        SAVE = True

    if len(sys.argv) == 2 and sys.argv[1] == "--load": 
        LOAD = True

    processed_subset = []

    if not LOAD:

        if not os.path.isfile("./entire_state_v.lst"):
            os.system("wget http://69.64.83.144/~mi/download/20170512/FOIA_Voters.zip")
            os.system("unzip FOIA_Voters.zip")

        # Choose random subset of data
        in_file = "entire_state_v.lst"
        voter_lst = open(in_file, 'r')
        data = voter_lst.readlines()
        voter_lst.close()
        subset = choice(data, SAMPLE_SIZE, replace=False)

        processed_subset_json = None
        
        if SAVE:
            processed_subset_json = open("processed_subset.json", 'w+')

        for line in subset:
            voter = lst_format(line)
            add_lat_lon(voter)
            processed_subset.append(voter)

        if SAVE:
            processed_subset_json.write(json.dumps(processed_subset))
            processed_subset_json.close()
        
    else:
        processed_subset_json = open("processed_subset.json",)
        processed_subset = json.load(processed_subset_json)
        processed_subset_json.close()

    format_lat_lon = np.array([[voter["latitude"], voter["longitude"]] for voter in processed_subset])
    clustering = SpectralClustering(n_clusters=CLUSTERS).fit(format_lat_lon)

    for i in range(SAMPLE_SIZE):
        processed_subset[i]["cluster"] = int(clustering.labels_[i])

    output_json = open("output.json", 'w+')
    output_json.write(json.dumps(processed_subset))
    output_json.close()
    
    # TODO: plot the data
    df = pd.DataFrame(processed_subset)
    crs = {'init': 'epsg:4326'}
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    street_map = gpd.read_file('./michigan_administrative/michigan_administrative.shp')
    fig, ax = plt.subplots(figsize = (15, 15))
    out = street_map.plot(ax = ax, alpha=0.4, color='grey')
    geo_df[geo_df['cluster'] == 0].plot(ax=ax, markersize=20, color='blue', marker='o')
    geo_df[geo_df['cluster'] == 1].plot(ax=ax, markersize=20, color='red', marker='o')
    geo_df[geo_df['cluster'] == 2].plot(ax=ax, markersize=20, color='green', marker='o')

    fig = out.get_figure()  
    fig.savefig("map.png")  

if __name__ == "__main__":
    main()