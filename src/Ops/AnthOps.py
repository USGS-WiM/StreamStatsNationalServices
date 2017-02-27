#------------------------------------------------------------------------------
#----- AnthOps.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  AnthOps is a server class, AnthOps provides a combination of useful
#               anthropogenic functions and properties 
#          
#     usage:  calculating % LandCoverage or other enviromnetal characteristics orginating from human activity
#             
#
#discussion:  
#       

#region "Comments"
#11.30.2016 jkn - Created
#endregion

#region "Imports"
import traceback
import tempfile
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import json
from  WiMLib.SpatialOps import SpatialOps
from  WiMLib import Shared
from WiMLib.MapLayer import *

#endregion

class AnthOps(SpatialOps):
    #region Constructor and Dispose
    def __init__(self, workspacePath):     
        SpatialOps.__init__(self, workspacePath) 
        self.WorkspaceID = os.path.basename(os.path.normpath(workspacePath))
                
        self._sm("initialized AnthOps")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SpatialOps.__exit__(self, exc_type, exc_value, traceback)  
    #endregion 

    #region Methods 
    def getReservoirStorage(self):
        '''
        Computes the Reservoir storage from National Inventory of Dams (NID)
        [Storage per unit area]
        '''
        nidML = None
        result = {"ReservoirStorageSum":0}
        try:
            self._sm("Computing NID reservoir storage")
            nidML = MapLayer(MapLayerDef("nid"))

            arcpy.env.workspace = self._TempLocation
            if not nidML.Activated:
                raise Exception("maplayer could not be activated.")

            #set mask
            mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"] )
            if not arcpy.Exists(mask): raise Exception("Mask does not exist: "+mask)
#Changed for each basin characteristic
            totArea = self.getAreaSqMeter(mask)* Shared.CF_SQMETERS2SQKILOMETER
            #spatial overlay
            #cursor and sum
            with arcpy.da.SearchCursor(self.spatialOverlay(nidML.Dataset, mask), nidML.QueryField, spatial_reference=nidML.spatialreference) as source_curs:
                for row in source_curs:
                    val = WiMLib.Shared.try_parse(row[0], None)
                    result["ReservoirStorageSum"] += float(val)*Shared.CF_ACR2SQKILOMETER/totArea
                #next
            #end with
        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Anthops ReservoirStorage" +tb, "ERROR", 71)
            result["ReservoirStorageSum"] = float('nan')

        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getPercentImpervious(self):
        '''
        Computes the % impervious
        '''
        nlcdML = None
        result = {"percentImpervious":None}
        try:
            self._sm("Computing percentImpervious")
            nlcdML = MapLayer(MapLayerDef("nlcd"))

            arcpy.env.workspace = self._TempLocation
            if not nlcdML.Activated: 
                raise Exception("maplayer could not be activated.")

            #set mask
            mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
            if not arcpy.Exists(mask): raise Exception("Mask does not exist: "+mask)
            result["percentImpervious"] = self.getRasterStatistic(nlcdML.Dataset, mask, "MEAN")

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Anthops percentImpervious" +tb, "ERROR", 71)
            result["percentImpervious"] = None

        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getPercentIrrigatedAgriculture(self):
        '''
        Computes the % Irrigated agriculture using MIRAD data
        '''
        miradML = None
        result = {"percentIrrigated":None}
        try:
            self._sm("Computing % irrigated ag")
            miradML = MapLayer(MapLayerDef("mirad2002"))

            arcpy.env.workspace = self._TempLocation
            if not miradML.Activated:
                raise Exception("maplayer could not be activated.")

            #set mask
            mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
            if not arcpy.Exists(mask): raise Exception("Mask does not exist: "+mask)

            result["percentIrrigated"]= self.getRasterPercent(miradML.Dataset, mask, "1")

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(),'AHMSG')
            self._sm("Anthops percentIrrigated" +tb,"ERROR", 71)
            result["percentIrrigated"] = None

        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getPercentMining(self):
        '''
        Computes the % Mined using nwalt dataset
        '''
        nwaltML = None
        result = {"percentMining2012":None}
        try:
            self._sm("Computing % mining")
            nwaltML = MapLayer(MapLayerDef("nwalt2012"))

            arcpy.env.workspace = self._TempLocation
            if not nwaltML.Activated:
                raise Exception("maplayer could not be activated.")

            #set mask
            mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
            if not arcpy.Exists(mask): raise Exception("Mask does not exist: "+mask)

            result["percentMining2012"]= self.getRasterPercent(nwaltML.Dataset, mask, "41")

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Anthops percentMining2012" +tb, "ERROR", 71)
            result["percentMining2012"] = None

        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getMajorSiteDensity(self):
        '''
        Computes Major site density
        Still needs work
        '''
        npdesML = None
        result = {"siteCountSum":0}
        try:
            self._sm("Computing NPDES Count")
            npdesML = MapLayer(MapLayerDef("npdes"))

            arcpy.env.workspace = self._TempLocation
            if not npdesML.Activated:
                raise Exception("maplayer could not be activated.")

            #set mask
            mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
            if not arcpy.Exists(mask): raise Exception("Mask does not exist: "+mask)

            tot = self.getFeatureStatistic(npdesML.Dataset, mask, "COUNT", npdesML.QueryField)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Anthops ReservoirStorage" +tb, "ERROR", 71)
            result["ReservoirStorageSum"] = float('nan')

        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result

    #endregion

    #region Helper Methods
    #endregion