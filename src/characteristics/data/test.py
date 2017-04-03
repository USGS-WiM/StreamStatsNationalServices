import sys, getopt
import csv
import json

csv_rows = []
with open('characteristics/test.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    title = reader.fieldnames
    for row in reader:
        #working line: csv_rows.extend([{row[title[0]]:{ title[i]:row[title[i]] for i in range(1, len(title)) }, }])
        #print [row[title[0]]: {title[i]:row[title[i]] for i in range(1, len(title))}]
        #print "'" + row[title[0]] + "' : " + str({title[i]:row[title[i]] for i in range(1, len(title))}) + ","
        #print [{row[title[0]]:{title[i]:row[title[i]] for i in range(1, len(title))},}]
        print [row[title[0]]: {title[1]:row[title[1]], title[2]:row[title[2]], title[3]:row[title[3]], title[4]:row[title[4]]}]
        csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])