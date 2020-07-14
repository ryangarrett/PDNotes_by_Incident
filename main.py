#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 10:34:39 2020
@author: rgarrett
"""
import pd
import datetime
import json
import csv
import pandas
import copy

token = ''
userId = ''
hoursSince = 100

now = datetime.datetime.utcnow()
then = now - datetime.timedelta(hours=hoursSince)
since = then.replace(microsecond=0).isoformat()
until = now.replace(microsecond=0).isoformat()
params = {'since': since, 'until': until}

iles = pd.fetch_log_entries(token=token, params=params)
incidentsIDs = []
incidentsWithNotes =[]
incidents_f =[]
notesByIncident = {}
notes = []

for ile in iles:
    if ile['channel']['type'] == 'note' and ile['agent']['id'] == userId:
        iid = ile['incident']['id']
        if iid in notesByIncident:
            newNote = {
                "note": ile['channel']['summary'], 
                "note_added": ile['created_at']
            }
            nbi = notesByIncident[iid]["notes"].append(newNote)
        else:
            r = pd.request(token=token, endpoint='incidents/'+ iid)
            newNote = {
                "note": ile['channel']['summary'], 
                "note_added": ile['created_at']
            }
            incidents_j = {
                "incident_id": iid,
                "incident_created_at":  r['incident']['created_at'],
                "last_status_change": r['incident']['last_status_change_at'],
                "status": r['incident']['status'],
                "added_by": ile['agent']['id'],
                "notes": [newNote ] 
            }
            notesByIncident[iid]=incidents_j

incidents_list = []
for key in notesByIncident:
    data = notesByIncident[key]
    for note in data["notes"]:
        data["note"] = note["note"]
        data["note_added"] = note["note_added"]
        new_row = copy.copy(data)
        del new_row["notes"]
        incidents_list.append(new_row)


final_out = json.dumps(incidents_list)
csv_file = "Incidents_" + str(now)[0:10] + ".csv"
pdObj = pandas.read_json(final_out)
pdObj.to_csv(csv_file, index=False)
