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

#endregion

class NLDIServiceAgent(ServiceAgentBase.ServiceAgentBase):
    #region Constructor
    def __init__(self):
        ServiceAgentBase.ServiceAgentBase.__init__(self, Config()["NLDIService"])

        self._sm("initialized NLDIServiceAgent")
    #endregion
    #region Methods
    def getBasin(self, comID, isCatchmentLevel=False):
        try:
            #distance = "0" if isCatchmentLevel else ""
            #resource = "comid/{0}/navigate/UT/basin?distance={1}".format(comID,distance)

            distance = "gages_iii_catchments" if isCatchmentLevel else "gages_iii_basins"
            resource = "/{1}/{0}.json".format(comID, distance)

            results = self.Execute(resource)
            return json.loads(results)
        except:
            tb = traceback.format_exc()
            self._sm("NLDIService getBasin Error "+tb, "ERROR")
    #endregion
    #region Helper Methods
    #endregion
    