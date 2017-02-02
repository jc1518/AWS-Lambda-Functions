#!/usr/bin/env python
# Print Opsgenie schedule lambda function
# 14/12/2016 version 1.0 by Jackie Chen


from __future__ import print_function
import os
import sys
import requests
import datetime
import pytz

API_KEY = os.environ['OPSGENIE_API_KEY']
SCHEDULE = 'Unix_schedule'
tz = pytz.timezone('Australia/Sydney')


def time_delta(days):
    return str(datetime.datetime.now() - datetime.timedelta(days= days)).split(' ')[0]


def time_converter(yourtime):
    return datetime.datetime.fromtimestamp(yourtime/1000, tz).strftime('%Y-%m-%d %H:%M:%S')


def lambda_handler(event, context):
    schedule_name = SCHEDULE
    INTERVAL = '9'
    print ('Downloading schedule ' + schedule_name + ' ...')
    if isinstance(event['weeks'], int):
        INTERVAL = str(event['weeks'] + 1)
        if event['weeks'] <= 1:
            INTERVAL = '2'
        if event['weeks'] >= 100:
            INTERVAL = '100'
    url = 'https://api.opsgenie.com/v1/json/schedule/timeline?apiKey=' + API_KEY + \
          '&name=' + schedule_name + '&date=' + time_delta(7) + '%2000:00' \
          '&intervalUnit=weeks&interval=' + INTERVAL
    req = requests.get(url)
    schedule = list()
    secondary = ''
    for rotation in req.json()['timeline']['finalSchedule']['rotations']:
        schedule.append(time_converter(rotation['periods'][1]['startTime']) + ',' +
                        time_converter(rotation['periods'][2]['endTime']) + ',' +
                        rotation['periods'][1]['recipients'][0]['displayName'] + ',' +
                        rotation['periods'][0]['recipients'][0]['displayName'])
        secondary = rotation['periods'][1]['recipients'][0]['displayName']
        for period in rotation['periods']:
            if rotation['periods'].index(period) > 2:
                schedule.append(time_converter(period['startTime']) + ',' +
                                time_converter(period['endTime']) + ',' +
                                period['recipients'][0]['displayName'] + ',' +
                                secondary)
                secondary = period['recipients'][0]['displayName']
    schedule.pop(0)
    schedule.insert(0, "--Starting Time-------Ending Time--------Primary-------Secondary---")
    return schedule






