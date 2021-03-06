#------------------------------------------------------------------------------
#----- Characteristic.py ----------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Data holder
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:   01 DEC 2016 jkn - Created / Date notation edited by jw
#
#------------------------------------------------------------------------------

#region "Imports"
import json
from WIMLib import WiMLogging
from WIMLib.Config import Config
import os
#endregion
class Characteristic(object):
    #region Constructor
    def __init__(self,chardefname):
        try:
            CharObj = Config()["characteristics"][chardefname]
            if (not CharObj): return None

            self.ID =  CharObj["ID"]if ("ID" in CharObj) else 0
            self.Name = chardefname
            self.MapLayers = CharObj["MapLayers"] if ("MapLayers" in CharObj) else None
            self.Method = CharObj["Method"] if ("Method" in CharObj) else None
            self.UnitID = CharObj["UnitID"]if ("UnitID" in CharObj) else ""
            self.Procedure = CharObj["Procedure"]
            self.Description =  CharObj["Description"]if ("Description" in CharObj) else ""
            self.QueryField =  CharObj["QueryField"]if ("QueryField" in CharObj) else None
            self.ClassCodes =  CharObj["ClassCodes"]if ("ClassCodes" in CharObj) else None
            self.Count = CharObj["Count"] if ("Count" in CharObj) else None		
            self.Data = os.path.join(Config()["parentdirectory"], CharObj["Data"])if ("Data" in CharObj) else None
            self.MethField = CharObj["methodField"]if ("methodField" in CharObj) else None
            self.Field = CharObj["selectorField"]if ("selectorField" in CharObj) else None
            self.Operator = CharObj["Operator"]if ("Operator" in CharObj) else None
            self.Keyword = CharObj["Keyword"]if ("Keyword" in CharObj) else None
            self.Variables = CharObj["Variables"]if ("Variables" in CharObj) else None
            self.Equation = CharObj["Equation"]if ("Equation" in CharObj) else None
            self.EquationVariables = CharObj["EquationVariables"]if ("EquationVariables" in CharObj) else None
            self.SubProcedure = CharObj["SubProcedure"]if ("SubProcedure" in CharObj) else None
            self.WhereClause = CharObj["WhereClause"]if ("WhereClause" in CharObj) else ""
            self.MultiplicationFactor = CharObj["MultiplicationFactor"] if ("MultiplicationFactor" in CharObj) else 1 # Added by JWX
            self.TimeRange = CharObj["TimeRange"] if ("TimeRange" in CharObj) else "" 
            self.TimeMethod = CharObj["TimeMethod"] if ("TimeMethod" in CharObj) else ""
            self.AggregationMethod = CharObj["AggregationMethod"] if ("AggregationMethod" in CharObj) else "weighteddifference" #seeWIMLib.ExpressionOps
            self.IDX = CharObj["IDX"] if ("IDX" in CharObj) else ""
            self.TOT_IDX = CharObj["TOT_IDX"] if ("TOT_IDX" in CharObj) else "",
            self.JoinTables = CharObj["JoinTables"] if ("JoinTables" in CharObj) else None,
            self.JoinField = CharObj["JoinField"] if ("JoinField" in CharObj) else None
        
        except:
            WiMLogging.sm(chardefname + " not available to compute. Returning none value.", "ERROR")
            return None
    #endregion
