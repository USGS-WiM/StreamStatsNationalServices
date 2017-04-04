#------------------------------------------------------------------------------
#----- ServiceAgent.py --------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Data retrieval code
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#
#      dates:   18 JUL 2016 jkn - Created / Date notation edited by jw
#
#------------------------------------------------------------------------------

#region "Imports"
import glob, sys, os
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
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.BaseUrl = None
    #endregion

    #region Methods
    def Execute(self, resource):
        try:
            url = self.BaseUrl + resource
            #below is temporary for batch jkn
            try:
                return json.dumps(json.load(open(url)))
                response = requests.get(url)
                return response.text
            except:
                self._sm("Error: file " + os.path.basename(resource) + " does not exist within Gages iii", 1.62, 'ERROR')
                return ''
        except requests.exceptions as e:
             if hasattr(e, 'reason'):
                self._sm("Error:, failed to reach a server " + e.reason.strerror, 1.54, 'ERROR')
                return ""

             elif hasattr(e, 'code'):
                self._sm("Error: server couldn't fullfill request " + e.code, 1.58, 'ERROR')
                return ''
        except:
            tb = traceback.format_exc()            
            self._sm("url exception failed " + resource + ' ' + tb, 1.60, 'ERROR')
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