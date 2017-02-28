import os
import datetime

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

'''
def convert unit(in unit, out unit)
    if this
    then this unit

    if this
    then out this unit
    switch(in_unit,out_unit) #LOOK THIS UP
'''