
#------------------------------------------------------------------------------
#----- Delineate.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Delineate using mask using arcpy
#          
#discussion:  https://github.com/GeoJSON-Net/GeoJSON.Net/blob/master/src/GeoJSON.Net/Feature/Feature.cs
#             http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/watershed.htm
#             geojsonToShape: http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/asshape.htm
#       

#region "Comments"
#08.19.2015 jkn - Created
#endregion

#region "Imports"
import traceback
import datetime
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import json
import WiMLib.WiMLogging
from WiMLib.Config import Config
#endregion

class MapLayer(object):
    #region Constructor
    def __init__(self, mlayerDef, tileID = "", queryfeature = None):
        self.ID =  mlayerDef.ID
        self.Description =  mlayerDef.Description
        self.Name =  mlayerDef.Name
        self.IsTiled = mlayerDef.IsTiled
        self.Path =  mlayerDef.Path
        self.QueryFeaturePath = mlayerDef.QueryFeaturePath
        self.QueryField = mlayerDef.QueryField
        self.TileID = tileID
        self.DatasetType = mlayerDef.DatasetType
        self.DatasetName = mlayerDef.DataSetName
        self.__queryfeature = queryfeature
   
        self.Activated = False

        self.Dataset = None
        self.spatialreference = None
        self.__Activate()
        #endif
    #endregion
    #region Helper Methods
    def __Activate(self):
        datasetPath =""
        try:
            if self.Activated: return

            if not os.path.isdir(self.Path): 
                self.canActivate = False    
                raise Exception(self.Name +" path doesn't exist")

            if self.IsTiled:
                self.__setTiledDatasetPath()
            
            if self.DatasetType.lower() == "esri_shape": self.Name += ".shp"      
            if self.DatasetType.lower() == "image_raster": self.Name += ".img"  
            
            datasetPath = os.path.join(self.Path,self.DatasetName,self.Name)   
            #check if dataset exists
            if not arcpy.Exists(datasetPath):
                raise Exception(datasetPath +" doesn't exist")

            self.Dataset = datasetPath
            self.spatialreference = arcpy.Describe(datasetPath).spatialReference
            self.Activated = True;
        except:
            tb = traceback.format_exc()
            self.Activated = False
    
    #endregion   
        
    #region Methods   
    #endregion      
    #region Helper Methods
    def __setTiledDatasetPath(self):
        row = None
        cursor = None
        selectlyr = None

        try:
            if self.TileID != "":
                return os.path.join(self.Path,self.TileID,self.Name)
            elif self.QueryFeaturePath:
                arcpy.MakeFeatureLayer_management(os.path.join(self.Path,self.QueryFeaturePath), "select_lyr")
                selectlyr = arcpy.SelectLayerByLocation_management("select_lyr","INTERSECT", self.__queryfeature)
                cursor = arcpy.da.SearchCursor(selectlyr[0],self.QueryField)
                for row in cursor:
                    # if you want all values in the field
                    self.Path = os.path.join(self.Path,row[0])
                #end for

        except:
            tb = traceback.format_exc()
            return ""
            msg = tb 
        finally:
            if row != None: del row
            if cursor != None: del cursor
            if selectlyr != None: del selectlyr  
                       
    #endregion

class MapLayerDef(object):
    #region Constructor
    def __init__(self,mldefname):
         
        maplayerObj = Config()["maplayers"][mldefname]
       
        self.ID =  maplayerObj["ID"]
        self.Description =  maplayerObj["Description"]
        self.Name =  maplayerObj["Name"]
        self.IsTiled = maplayerObj["isTiled"]
        self.Path =  maplayerObj["path"]
        self.QueryFeaturePath = maplayerObj["queryFeaturePath"] if ("queryFeaturePath" in maplayerObj) else None
        self.QueryField = maplayerObj["queryField"] if ("queryField" in maplayerObj) else None
        self.DataSetName = maplayerObj["DataSetName"] if ("DataSetName" in maplayerObj) else ""
        self.DatasetType =  maplayerObj["DatasetType"]    

    #endregion