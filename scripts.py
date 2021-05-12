import json
import os
import sys
from numpy.random import choice
from geopy.geocoders import GoogleV3

api_file = open('API', 'r')
geolocator = GoogleV3(api_key=api_file.readline())

SAVE = False
LOAD = False

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
            "complete_address": None,
            "latitude": None,
            "longitude": None,
        }
    return voter

def main():
    if len(sys.argv) > 2: 
        print("Error: Too many arguments")

    if len(sys.argv) == 2 and sys.argv[1] == "--save": 
        SAVE = True

    if len(sys.argv) == 2 and sys.argv[1] == "--load": 
        LOAD = True

    if not os.path.isfile("./entire_state_v.lst"):
        os.system("wget http://69.64.83.144/~mi/download/20170512/FOIA_Voters.zip")
        os.system("unzip FOIA_Voters.zip")

    # Choose random subset of data
    in_file = "entire_state_v.lst"
    voter_lst = open(in_file, 'r')
    data = voter_lst.readlines()
    voter_lst.close()
    subset = choice(data, 20000, replace=False)

    processed_subset = []
    processed_subset_json = None
    
    if SAVE:
        out_file = "processed_subset.json"
        processed_subset_json = open(out_file, 'w+')

    for line in subset:
        voter = lst_format(line)
        add_lat_lon(voter)
        processed_subset.append(voter)

        if SAVE:
            processed_subset_json.write(json.dumps(voter))

    if SAVE:
        processed_subset_json.close()

    # TODO: convert into lat, lon pairs and use spectral clustering
    # TODO: allow for loading from old json data

if __name__ == "__main__":
    main()