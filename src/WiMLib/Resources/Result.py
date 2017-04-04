#------------------------------------------------------------------------------
#----- Result.py --------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Data holder code
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:  01 DEC 2016 jkn - Created / Date notation edited by jw
#
#------------------------------------------------------------------------------

#region "Imports"
import json
#endregion
class Result(object):
    def __init__(self,identifier,descr = ""):
        self.ID = identifier
        self.Description = descr
        self.Values = {}