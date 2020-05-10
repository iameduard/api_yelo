#!/usr/bin/python3
import json
import csv
import oauth2client
import gspread
from   oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
##############################################
# Google Drive API...
##############################################
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds02.json', scope)
client = gspread.authorize(creds)
sheet_schedule = client.open('schedule').worksheet('scripts')
now = datetime.now()
schedule = sheet_schedule.get_all_records()
weekday=now.strftime("%a").upper()
H24=now.strftime("%H%p")
for script in schedule:
    if H24 in script.get(weekday):
        print(script['SCRIPT'],'-',str(now))
        os.system(python3 script['SCRIPT'])
sheet_executions = client.open('schedule').worksheet('executions')
executions = sheet_executions.get_all_records()
sheet_executions.update_cell(len(executions)+2, 1, str(now))

