#------------------------------------------------------------------------------
#----- Shared.py --------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM) ??????
#              
#    purpose:  THIS SECTION NEEDS TO BE UPDATED
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:  THIS SECTION NEEDS TO BE UPDATED
#
#------------------------------------------------------------------------------

import os
import sys
import datetime
from WiMLib import WiMLogging
import traceback
import string
import csv

CF_ACR2SQKILOMETER = 0.00404685642              # 1 acres = 0.00404685642 square kilometers
CF_SQMETERS2SQKILOMETER = 0.000001              # 1 square meter = 1.0 x 10-6 square kilometers

def GetWorkspaceDirectory(workingdirectory, projID="", workspaceID=""):

    if(workspaceID ==""):
                workspaceID = projID + str(datetime.datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')

    WorkspaceDirectory = os.path.join(workingdirectory, workspaceID)
    if not os.path.exists(WorkspaceDirectory):
        os.makedirs(WorkspaceDirectory)

    return WorkspaceDirectory

def parse(string):
    try:
        return float(string)
    except Exception:
        return TypeError

def try_parse(string, fail=None):
    try:
        return float(string)
    except Exception:
        return fail;
def readCSVFile( file):
    #https://docs.python.org/2/library/csv.html
    f = None
    try:
        if (not os.path.isfile(file)):
            return []
        f = open(file, 'r')
       # csv.field_size_limit(sys.maxsize)
        return map(lambda s: s, csv.reader(f))
    except:
        tb = traceback.format_exc()
        WiMLogging.sm("Error reading csv file "+tb)
    finally:
        if not f == None:
            if not f.closed :
                f.close();
def appendLineToFile(file, content):
    f = None
    try:
        f = open(file, "a")            
        f.write(string.lower(content + '\n'))
    except:
        tb = traceback.format_exc()
        WiMLogging.sm("Error appending line to file "+tb)

    finally:
        if not f == None or not f.closed :
            f.close();
def writeToFile(file, content):
    f = None
    try:
        f = open(file, "w")
        f.writelines(map(lambda x:x+'\n', content))
    except:
        tb = traceback.format_exc()
        WiMLogging.sm("Error writing to file "+tb)
    finally:
        if not f == None or not f.closed :
            f.close();