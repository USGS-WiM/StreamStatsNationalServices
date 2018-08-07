#------------------------------------------------------------------------------
#----- NLDIServiceAgent.py ----------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  NLDIServiceAgent is a server class to provide hunting and gathering  
#                   methods for NLDI service
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#
#      dates:   09 DEC 2016 jkn - Created / Date notation edited by jw
#
#------------------------------------------------------------------------------

#region "Imports"
import traceback
import json
from WIMLib.Resources import *
from WIMLib.ServiceAgents import ServiceAgentBase
from WIMLib.Config import Config
from WIMLib import GeoJsonHandler
from WIMLib import Shared
import os

#endregion

class NLDIFileServiceAgent(ServiceAgentBase.ServiceAgentBase):
    #region Constructor
    def __init__(self):
        ServiceAgentBase.ServiceAgentBase.__init__(self, Config()["NLDIServiceFiles"])

        self._sm("initialized NLDIFileServiceAgent")
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ServiceAgentBase.ServiceAgentBase.__exit__(self, exc_type, exc_value, traceback) 
    #endregion
    #region Methods
    def getBasin(self, comID, isCatchmentLevel=False, xpoint = None, ypoint = None, crs = 4326):
        try:
            distance = "gages_iii_catchments" if isCatchmentLevel else "gages_iii_basins"
            resource = "/{1}/{0}.json".format(comID, distance)

            try:
                url = self.BaseUrl + resource
                results = json.dumps(json.load(open(url)))
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
            resource = Config()['queryParams']['nldiChars'].format(comID)
            
            results = json.loads(self.Execute(resource))
            
            for x in results['characteristics']:
                results[str(x['characteristic_id'])] = x['characteristic_value']
            
            return results
        except:
            tb = traceback.format_exc()
            self._sm("NLDIService getBasinCharacteristics Error "+tb, "ERROR")

    #endregion
    #region Helper Methods
    #endregion
    