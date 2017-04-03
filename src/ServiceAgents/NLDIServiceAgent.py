#------------------------------------------------------------------------------
#----- NLDIServiceAgent.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  NLDIServiceAgent is a server class, to provide hunting and gathering  
#               methods for NLDI service
#     usage:  
#             
#
#discussion:  
#       

#region "Comments"
#12.09.2016 jkn - Created
#endregion

#region "Imports"
import traceback
import json
from WiMLib.Resources import *
from WiMLib.ServiceAgents import ServiceAgentBase
from WiMLib.Config import Config
from WiMLib import GeoJsonHandler
from WiMLib import Shared
import os

#endregion

class NLDIServiceAgent(ServiceAgentBase.ServiceAgentBase):
    #region Constructor
    def __init__(self):
        ServiceAgentBase.ServiceAgentBase.__init__(self, Config()["NLDIService"])

        self._sm("initialized NLDIServiceAgent")
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ServiceAgentBase.ServiceAgentBase.__exit__(self, exc_type, exc_value, traceback) 
    #endregion
    #region Methods
    def getBasin(self, comID, isCatchmentLevel=False):
        try:
            #distance = "0" if isCatchmentLevel else ""
            #resource = "comid/{0}/navigate/UT/basin?distance={1}".format(comID,distance)

            distance = "gages_iii_catchments" if isCatchmentLevel else "gages_iii_basins"
            resource = "/{1}/{0}.json".format(comID, distance)

            #Should these lines be included?
            #results = self.Execute(resource)
            #return json.loads(results)

            try:
                results = self.Execute(resource)
                return json.loads(results)
            except:
                tb = traceback.format_exc()
                self._sm("Exception raised for "+ os.path.basename(resource) + ". Moving to next ComID.", "ERROR")
        except:
            tb = traceback.format_exc()
            self._sm("NLDIService getBasin Error "+tb, "ERROR")
    def getBasinCharacteristics(self,comID):
        results={}
        try:
            #resource = "comid/{0}/navigate/UT/basin?distance={1}".format(comID,distance)
            resource = "gagesIII_mw_characteristics_{0}.csv".format("tot")
            #Temp solution until they get the services up and running
            file = Shared.readCSVFile(os.path.join(self.BaseUrl,resource))
            headers = file[0]
            file.pop(0)
            comIDindex = headers.index('COMID')           
            for row in file:
                if(len(row) < comIDindex): continue
                if comID == row[comIDindex]:
                    for h in headers:
                       results[h] = row[headers.index(h)]
                       break
                    #next h
                    return results
               #endif
            #next row
            return None
        except:
            tb = traceback.format_exc()
            self._sm("NLDIService getBasinCharacteristics Error "+tb, "ERROR")

    #endregion
    #region Helper Methods
    #endregion
    