from itertools import zip_longest
from ratelimit import limits, sleep_and_retry

import requests
import os
import json


def get_reonomy_auth():
    return (os.environ['REONOMY_ID'], os.environ['REONOMY_PASSWORD'])

def read_input(filename, ):
    with open(filename) as f:
        return f.readlines()

def grouper(iterable):
    args = [iter(iterable)] * 2
    return zip_longest(*args)

def convert_to_polygons(lines):
    polygons = map(lambda s: s.split(), lines)
    return map(lambda p: list(grouper(p)), polygons)

def create_search_request(polygon):
    return {
        "search": {
            "geo": {
            "polygons": [
                {
                "coordinates": [ polygon ]
                }
            ]
            }
        },
        "per_page": 50,
        "page": 1
    }

def extract_property_ids(response):
    return list(map(lambda d: d["id"], response["results"]))

@sleep_and_retry
@limits(calls=20, period=60)
def make_search_request(request):
    resp = requests.post("https://api.reonomy.com/v1/properties/search", json=request, auth=get_reonomy_auth())
    resp.raise_for_status()
    return extract_property_ids(resp.json())

@sleep_and_retry
@limits(calls=20, period=60)
def fetch_property_details(property_id):
    print(f"Processing property: {property_id}")
    resp = requests.get(f"https://api.reonomy.com/v1/properties/{property_id}", auth=get_reonomy_auth())
    resp.raise_for_status()
    with open(f"./results/{property_id}", "w") as f:
        f.write(json.dumps(resp.json(), indent=4))

def main():
    print("Creating a directory to store results in current folder")
    os.mkdir("./results")

    print("Reading polygon specifications from file polygons.tsv, each line in the file represents a polygon specification")
    polygons = convert_to_polygons(read_input('polygons.tsv'))
    
    print("Invoking search request using the polygon specification, we will fetch upto 50 properties for each search")
    reqs = map(lambda p : create_search_request(p), polygons)
    properties_for_polygon = map(lambda r : make_search_request(r), reqs)

    print("Fetching property details and writing to file in results folder")
    print("MAX OF 30 REQUESTS PER MINUTE, SLEEPING IF NECESSARY")
    for properties in properties_for_polygon:
        for pid in properties:
            fetch_property_details(pid)


main()