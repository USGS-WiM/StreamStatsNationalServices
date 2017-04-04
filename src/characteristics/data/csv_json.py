#------------------------------------------------------------------------------
#----- csv_json.py ----------------------------------------------
#------------------------------------------------------------------------------
#
# copyright:   2017 WiM - USGS (probably should not have this)
#
#    authors:  John Wall - Ph.D. Student NC State University
#
#    purpose:  This code is intended to convert characterisitcs identified by
#                   Tana Haluska (thaluska@usgs.gov) and inventoried to
#                   CatchmentVars.Metadata.xlsx to JSON format for config.json
#
#      usage:  Converts CSV to JSON
#
# discussion:  The XLSX file above was cleaned by John Wall and converted to
#                   CSV. This CSV is what is then processed. Attributes needed
#                   from the file include ID, Description, and Units.
#                   The config.json file would also like to have procedure and
#                   map layer(s) which should be defined by manual entry.
#
#               This code was ripped from a blog and only minorly changed
#
#      dates:   15 MAR 2017
#
#  resources:   http://www.idiotinside.com/2015/09/18/csv-json-pretty-print-python/
#
#------------------------------------------------------------------------------

import sys, getopt
import csv
import json

#Get Arguments
def main(argv):
    input_file = 'characteristics/test.csv'
    output_file = 'characteristics/json.txt'
    format = 'pretty'
    try:
        opts, args = getopt.getopt(argv,"hi:o:f:",["ifile=","ofile=","format="])
    except getopt.GetoptError:
        print 'csv_json.py -i <path to inputfile> -o <path to outputfile> -f <dump/pretty>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'csv_json.py -i <path to inputfile> -o <path to outputfile> -f <dump/pretty>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-f", "--format"):
            format = arg
    read_csv(input_file, output_file, format)

#Read CSV File
def read_csv(file, json_file, format):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            #The line below needs to be fixed to output correctly for the JSON Dumps function
            csv_rows.extend([{row[title[0]]: {title[i]:row[title[i]] for i in range(1, len(title))}}])
        write_json(csv_rows, json_file, format)

#Convert csv data into json and write it
def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        if format == "pretty":
            f.write(json.dumps(data, sort_keys=False, indent=2, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
        else:
            f.write(json.dumps(data))

if __name__ == "__main__":
   main(sys.argv[1:])