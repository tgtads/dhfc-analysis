#!/usr/bin/python

import datetime
from tzwhere import tzwhere
tz = tzwhere.tzwhere()
import pytz
import re

def get_utc(lat, lon, dstr):
    # best practice is to ignore reported offset and calculate it from lat and lon
    timezone_str = tz.tzNameAt(lat, lon) # coordinates
    try:
        timezone = pytz.timezone(timezone_str)
        (year, month, day, hour, minute, second) = map(int, re.split(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\+[0-9]{4}", dstr)[1:-1])
        # inner index used because https://docs.python.org/2/library/re.html#module-contents for re.split()
        # map used to convert to int
        local = datetime.datetime(year, month, day, hour, minute, second)
        utc = (local - timezone.utcoffset(local)).replace(tzinfo=timezone)
        return utc
    except AttributeError as e:
        print("Error [%s] with timezone:[%s], lat:[%s], lon:[%s]" % (e, timezone_str, lat, lon))


def test():
    return get_utc(lat=50.869041443, lon=0.01225, dstr="2016-02-10T19:45:00+0000")
