#------------------------------------------------------------------------------
#----- ServiceAgent.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Data retrieval code 
#          
#discussion:  
#

#region "Comments"
#07.18.2010 jkn - Created
#endregion

#region "Imports"
import glob, sys
import requests
import certifi
import json
import string
import traceback
from  WiMLib import WiMLogging
import re

from datetime import date, timedelta
#endregion

class ServiceAgentBase(object):
    """ """
    #region Constructor
    def __init__(self,baseurl):
        self.BaseUrl = baseurl

    #endregion

    #region Methods
    def Execute(self, resource):
        try:
            url = self.BaseUrl + resource
            #below is temporary for batch jkn
            return json.dumps(json.load(open(url)))
            response = requests.get(url)
            return response.text
        except requests.exceptions as e:
             if hasattr(e, 'reason'):
                self.__sm("Error:, failed to reach a server " + e.reason.strerror, 1.54, 'ERROR')
                return ""

             elif hasattr(e, 'code'):
                self.__sm("Error: server couldn't fullfill request " + e.code, 1.58, 'ERROR')
                return ''
        except:
            tb = traceback.format_exc()            
            self.__sm("url exception failed " + resource + ' ' + tb, 1.60, 'ERROR')
            return ""    
    
    def indexMatching(self, seq, condition):
        for i,x in enumerate(seq):
            if condition(x):
                return i
        return -1

    def _sm(self,msg,type="INFO", errorID=0):        
        WiMLogging.sm(msg,type="INFO", errorID=0)
        
    #endregion
#end class