#------------------------------------------------------------------------------
#----- Characteristic.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#   authors:  Jeremy K. Newson USGS Wisconsin Internet Mapping
#
#   purpose:   Data holder
#
#discussion:
#

#region "Comments"
#12.01.2016 jkn - Created
#endregion

#region "Imports"
import json
from WiMLib.Config import Config
#endregion
class Characteristic(object):
    #region Constructor
    def __init__(self,chardefname):

        CharObj = Config()["characteristics"][chardefname]
        if (not CharObj): return None

        self.ID =  CharObj["ID"]if ("ID" in CharObj) else 0
        self.Name = chardefname
        self.MapLayers = CharObj["MapLayers"]      
        self.Method = CharObj["Method"] if ("Method" in CharObj) else None
        self.UnitID = CharObj["UnitID"]if ("UnitID" in CharObj) else ""
        self.Procedure = CharObj["Procedure"]
        self.Description =  CharObj["Description"]if ("Description" in CharObj) else ""
        self.QueryField =  CharObj["QueryField"]if ("QueryField" in CharObj) else None
        self.ClassCodes =  CharObj["ClassCodes"]if ("ClassCodes" in CharObj) else None
        self.Count = CharObj["Count"] if ("Count" in CharObj) else None
    #endregion