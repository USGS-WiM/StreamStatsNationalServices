#------------------------------------------------------------------------------
#----- characteristicsWrapper.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  merge catchment with global basin 
#          
#discussion:  #https://docs.google.com/document/d/1vADDaCya_XXsXCupiFpXeGMnGLbSognJUOmdhEo30HU/edit
#       

#region "Comments"
#12.01.2016 jkn - Created
#endregion

#region "Imports"
import traceback
import datetime
import time
import os
import argparse
import arcpy
from arcpy import env
from Ops.GeogOps import *
from Ops.AnthOps import *
from Ops.PhysOps import *
from Ops.HydroOps import *
from WiMLib.SpatialOps import *
from WiMLib import WiMLogging
from WiMLib.Resources import  Result
import json

#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
#http://stackoverflow.com/questions/13653991/passing-quotes-in-process-start-arguments
class CharacteristicsWrapper(object):
    #region Constructor
    def __init__(self):
        WiMResults = None
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-workspaceID", help="specifies the split catchment workspace", type=str, default="FH20170130141235512000")           
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "DRNAREA;KSATSSUR;I24H10Y;CCM;TAU_ANN;STREAM_VAR;PRECIP;HYSEP;RSD")                 
            args = parser.parse_args()

            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'))))  
            workspaceID = args.workspaceID
            workingDir = os.path.join(Config().getElement("workingdirectory"),workspaceID)   

            if not os.path.exists(workingDir):
                raise Exception('workspaceID is invalid') 
                 
            WiMLogging.init(os.path.join(workingDir,"Temp"),"mergeCatchment.log")
            WiMResults = Result.Result("Characteristics computed for "+workspaceID)

            startTime = time.time()
            with AnthOps(workingDir) as aOps: 
                WiMResults.Values.update(aOps.getMajorSiteDensity())
                WiMResults.Values.update(aOps.getReservoirStorage())
                WiMResults.Values.update(aOps.getPercentMining())               
                WiMResults.Values.update(aOps.getPercentIrrigatedAgriculture())                
                WiMResults.Values.update(aOps.getPercentImpervious())
                
            with HydroOps(workingDir) as hyOps:
                WiMResults.Values.update(hyOps.getFreshWaterWithdrawals())

            print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'
            
            Results = {
                       "Workspace": aOps.WorkspaceID,
                       "Message": ';'.join(WiMLogging.LogMessages).replace('\n',' '),
                       "Results": WiMResults
                      }
        except:
             tb = traceback.format_exc()
             Results = {
                       "error": {"message": traceback.format_exc()}
                       }
        finally:
            print "Results="+json.dumps(Results,default=lambda o: o.__dict__) 
            print "Done"
    
if __name__ == '__main__':
    CharacteristicsWrapper()

