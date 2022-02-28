import pandas as pd
import numpy as np
import datetime
import csv

deadline = datetime.datetime(2022, 2, 11, 23, 59, 59)
num_late_days = 2


results = pd.read_csv("aX_latest.csv")
results.drop(results.columns[[1,3,4,5,6,7,8,9,]], axis=1, inplace=True)
results['submitted'] = pd.to_datetime(results['submitted'], format="%a, %d %b %Y %H:%M:%S EST")
results = results[results['submitted']<=(deadline + datetime.timedelta(days = num_late_days))]
results.drop_duplicates(subset=['email'], inplace=True)

results['total'] = results.sum(axis=1)

conditions = [
    (results['submitted'] <= deadline),
    (results['submitted'] > deadline) & (results['submitted'] <= deadline + datetime.timedelta(days = 1)),
    (results['submitted'] > deadline + datetime.timedelta(days = 1))
]

penalties = [0, 10, 20]
results['penalty'] = np.select(conditions, penalties)
# # results['total'] = results['total'].clip(lower=0)

with open('classlist.csv', mode='r') as inp:
    reader = csv.reader(inp)
    email_id_dict = {rows[2]:rows[0] for rows in reader}

with open('classlist.csv', mode='r') as inp:
    reader = csv.reader(inp)
    username_dict = {rows[1][1:]:rows[0] for rows in reader}

results['OrgDefinedId'] = results['email'].map(lambda x : email_id_dict[x] if x in email_id_dict else username_dict[x])
final = results[['OrgDefinedId', 'total', 'penalty']]
final['End-of-Line Indicator'] = "#"
# # final['penalty'] = -1*final['penalty']

final=final.rename(columns = {
    'total':'Assignment X Points Grade <Numeric MaxPoints:100 Weight:10>',
    'penalty':'AX late penalty Points Grade <Numeric MaxPoints:20 Weight:0>'
})
final.to_csv('aX_grades.csv',index=False)
