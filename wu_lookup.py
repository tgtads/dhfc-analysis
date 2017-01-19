#!/usr/bin/python

import requests # in py 2.7, use requests
import re
import csv
from collections import defaultdict

# perhaps this can be extended to use the twisted networking protocol
# the dayfiles are in local date form, NOT UTC


# cleanly return the results of a web request

def req(url):
    try:
        return requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error [%s] with [%s]" % (e, url))

# specific to this website's output

def body_to_dict(responseObj):
    lines = []
    for rawline in responseObj.iter_lines(decode_unicode=True):
        rawline = re.sub("<br />", "", rawline)
        if rawline:
            lines.append(rawline)
    header = lines.pop(0)
    if re.search("Conditions", header) and not re.search("No daily or hourly history data available", lines[0]):
        dictObjs = []
        for line in csv.DictReader(lines, fieldnames=re.split(",", header)):
            dictObjs.append(line)
        return dictObjs

# returns a dictionary

def get_data(station_name, y, m, d):
    s = "https://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?format=1" % (station_name, y, m, d)
    responseObj = req(s)
    if responseObj:
        return body_to_dict(responseObj)

def test_wu():
    return get_data(station_name="EGLL", y=2016, m=02, d=10)
