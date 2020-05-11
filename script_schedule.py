#!/usr/bin/python3
import json
import csv
import oauth2client
import gspread
import os
import sys
from   oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
##############################################
# Google Drive API...
##############################################
orig_stdout = sys.stdout
now = datetime.now()
f = open('out_'+datetime.now().strftime('%Y_%m_%d_%H')+'.txt', 'a')
sys.stdout = f
print('Fecha de ejecucion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds02.json', scope)
client = gspread.authorize(creds)
sheet_schedule = client.open('schedule').worksheet('scripts')
schedule = sheet_schedule.get_all_records()
sheet_executions = client.open('schedule').worksheet('executions')
executions = sheet_executions.get_all_records()
now = datetime.now()
weekday=now.strftime("%a").upper()
H24=now.strftime("%H%p")
for script in schedule:
	if H24 in script.get(weekday):
		job = str(datetime.now())+'|'+script['SCRIPT']
		sheet_executions.update_cell(len(executions)+2, 1, job)
		os.system('python3 '+script['SCRIPT'])

print('Fecha de culminacion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))
sys.stdout = orig_stdout
f.close()


