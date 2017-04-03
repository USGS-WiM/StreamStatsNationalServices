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
from Ops.StreamStatsNationalOps import *
from WiMLib.SpatialOps import *
from WiMLib import WiMLogging
from Resources import Characteristic
from WiMLib.Resources import Result
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
            parser.add_argument("-workspaceID", help="specifies the split catchment workspace", type=str, default="FH20170313102909483000") #Change default           
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "")                 
            args = parser.parse_args()

            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'))))  
            self.workspaceID = args.workspaceID
            self.workingDir = os.path.join(Config().getElement("workingdirectory"),self.workspaceID)   

            if not os.path.exists(self.workingDir):
                raise Exception('workspaceID is invalid') 
            if(args.parameters): self.params =  args.parameters.split(";") 
            #get all characteristics from config
            else: self.params =  config["characteristics"].keys() 
          
            
            WiMLogging.init(os.path.join(self.workingDir,"Temp"),"mergeCatchment.log")
            
        except:
             tb = traceback.format_exc()
             self._sm(tb + "Failed to initialize","Error")
             return None             
    def Execute(self):
        method = None
        try:
            WiMResults = Result.Result("Characteristics computed for "+self.workspaceID)

            startTime = time.time()
            with StreamStatsNationalOps(self.workingDir,self.workspaceID) as sOps: 
                for p in self.params:
                    method = None
                    parameter = Characteristic.Characteristic(p)
                    if(not parameter): 
                        self._sm(p +"Not available to compute")
                        continue

                    method = getattr(sOps, parameter.Procedure) 
                    if (method): WiMResults.Values.update(method(parameter))  
                    else:
                        self._sm(p.Proceedure +" Does not exist","Error")
                        continue   
                            
                #next p
            #end with

            print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'
            
            Results = {
                       "Workspace": self.workspaceID,
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

    def _sm(self,msg,type="INFO", errorID=0):        
        WiMLogging.sm(msg,type="INFO", errorID=0)
if __name__ == '__main__':
    cw = CharacteristicsWrapper()
    cw.Execute()

