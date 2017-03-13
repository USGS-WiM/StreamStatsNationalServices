#------------------------------------------------------------------------------
#----- Result.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
# 
#   purpose:  Data holder
#          
#discussion:  
#

#region "Comments"
#12.01.2016 jkn - Created
#endregion

#region "Imports"
import json
#endregion
class Result(object):
    def __init__(self,identifier,descr = ""):
        self.ID = identifier
        self.Description = descr
        self.Values = {}