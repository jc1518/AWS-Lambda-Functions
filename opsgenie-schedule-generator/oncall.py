#!/usr/bin/env python
# Convert Opsgenie schedule to Excel spreadsheet
# 14/12/2016 version 1.0 by Jackie Chen


from __future__ import print_function
import os
import sys
import requests
import datetime
import xlsxwriter


API_KEY = os.environ['OPSGENIE_API_KEY']
NAME = 'Opsgenie_Schedule_Table'
SCHEDULE1 = 'Unix_schedule'
SCHEDULE2 = 'AWSOps_schedule'
INTERVAL = '8'


def time_delta(days):
    return str(datetime.datetime.now() - datetime.timedelta(days= days)).split(' ')[0]


def time_converter(yourtime):
    return datetime.datetime.fromtimestamp(yourtime/1000).strftime('%Y-%m-%d %H:%M:%S')


def get_schedule(schedule_name):
    print ('Downloading schedule ' + schedule_name + ' ...')
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
    for week in schedule:
        print (week)
    return schedule


def generate_xlsx(schedules):
    workbook = xlsxwriter.Workbook(NAME + '.xlsx')
    bold = workbook.add_format({'bold': True})
    merge_format = workbook.add_format({'align': 'center', 'bold': True, 'size': '18'})
    worksheet = workbook.add_worksheet()
    worksheet.merge_range('A1:I1', 'Opsgenie Support Roster / Support Phone#:XXXXXXX', merge_format)
    try:
        for schedule in schedules:
            row = 2
            schedule_name = schedule[0]
            col = schedule[1]
            postion = schedule[2]
            schedule = get_schedule(schedule_name)
            schedule.pop(0)
            print ('Generating spreadsheet for ' + schedule_name)
            worksheet.merge_range(postion, schedule_name, merge_format)
            worksheet.set_column(col, col + 3, 18)
            worksheet.write(row, col, 'Starting Time', bold)
            worksheet.write(row, col + 1, 'Ending Time', bold)
            worksheet.write(row, col + 2, 'Primary Support', bold)
            worksheet.write(row, col + 3, 'Secondary Support', bold)
            row += 1
            for week in schedule:
                worksheet.write(row, col, week.split(',')[0])
                worksheet.write(row, col + 1, week.split(',')[1])
                worksheet.write(row, col + 2, week.split(',')[2])
                worksheet.write(row, col + 3, week.split(',')[3])
                row += 1
        workbook.close()
        print ("Done!")
        return True
    except:
        print("Oops, something went wrong. " + str(sys.exc_info()[1]))
        return False


if __name__ == '__main__':
    schedules = [[SCHEDULE1, 0, 'A2:D2'], [SCHEDULE2, 5, 'F2:I2']]
    generate_xlsx(schedules)





