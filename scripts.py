import json
from geopy.geocoders import Nominatim

def address_to_coordinate():
    geolocator = Nominatim(user_agent="sample app")
    data = geolocator.geocode("1680 CHATHAM DR, TROY, MI 48084")
    print(data.point.latitude, data.point.longitude)

def lst_to_json():
    # Set input and output locations
    in_file = "code48084.lst"
    out_file = "code48084.json"
    voter_lst = open(in_file, 'r')
    voter_json = open(out_file, 'w+')

    # Iterate over every line of input
    for line in voter_lst:

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
        }

        voter_json.write(json.dumps(voter))

    voter_lst.close()
    voter_json.close()

def main():
    lst_to_json()
    #address_to_coordinate()

if __name__ == "__main__":
    main()