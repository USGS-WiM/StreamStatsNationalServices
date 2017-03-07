#------------------------------------------------------------------------------
#----- Result.py ----------------------------------------------------
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
class CharacteristicDef(object):
    #region Constructor
    def __init__(self,chardefname):

        CharacteristicObj = Config()["characteristics"][chardefname]

        self.ID =  CharacteristicObj["ID"]
        self.Name = CharacteristicObj["Name"]
        self.MapLayer = CharacteristicObj["MapLayer"]
        self.Description =  CharacteristicObj["Description"]
        self.Method = CharacteristicObj["Mehod"]
        self.UnitID = CharacteristicObj["UnitID"]
        self.ClassCode = CharacteristicObj["ClassCode"] if ("ClassCode" in CharacteristicObj) else None

        #I note in StreamStatsNationalOps.py that we could include a Count option for getPointFeatureDensity
        #   however this might be unnecessairy. I've included it here for completion.
        self.Count = CharacteristicObj["Count"] if ("Count" in CharacteristicObj) else None
    #endregion