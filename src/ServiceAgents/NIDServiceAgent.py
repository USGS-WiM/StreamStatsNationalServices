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

class NIDServiceAgent(ServiceAgentBase.ServiceAgentBase):
    #region Constructor
    def __init__(self):
        ServiceAgentBase.ServiceAgentBase.__init__(self, Config()["NLDIServiceFiles"])

        self._sm("initialized DamIndexServiceAgent")
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ServiceAgentBase.ServiceAgentBase.__exit__(self, exc_type, exc_value, traceback) 
    #endregion
    #region Methods
    def getDisturbanceIndex(self,comID):
        results={}
        key = comID+'.0'
        try:
            resource = Config()['queryParams']['damindex']
            url = self.BaseUrl + resource
            results = json.load(open(url))

            if(key in results):
                return results[key]
            else:
              return 0
            
        except:
            tb = traceback.format_exc()
            self._sm("NLDIService getBasinCharacteristics Error "+tb, "ERROR")

    #endregion
    #region Helper Methods
    #endregion
    