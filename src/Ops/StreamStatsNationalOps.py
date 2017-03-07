#------------------------------------------------------------------------------
#----- StreamStatsNationalOps.py ----------------------------------------------
#------------------------------------------------------------------------------
#
# copyright:   2016 WiM - USGS
#
#    authors:  John Wall - Ph.D. Student NC State University
#              Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#
#    purpose:  This code is intended to generalize functions found in prior work by
#                   Jeremy for current work as part of WiM's duties. Coding has been
#                   done by J. Wall so blame him if something looks weird.
#
#      usage:  Calculates various metrics
#
# discussion:  This work compresses the functions found in AnthOps, GeogOps,
#                   HydroOps, and PhysOps to generalized functions which are able
#                   to be called over and over again for various calculations/goals.
#
#              This was done by simply copy and pasting the code from each of
#                   these files into this one and then trimming until the minimum
#                   functions were left.
#
#              ACHTUNG! - variables found here have not been ensured to be the
#                         current ones used in any of the other scripts used
#                         for calculations. These will need to be updated.
#
#      dates:   30 NOV 2016 jkn - Created / Date notation edited by jw
#               27 FEB 2017 jw - Modified
#
#   mod work:   Pull from HydroOps - Tutorial with Jeremy (DONE)
#               AnthOps (DONE)
#               GeogOps (N/A)
#               PhysOps (N/A)
#
# sum of mod:   All unique functions in HydroOps and AnthOps were added to this
#                   class. As part of this addition, new passing variables were
#                   included in the functions. These passed variables come from
#                   config.json. Thus, config.json was updates to include these
#                   classes.
#
# add. notes:   Why not just define MapLayers/ML at the top? This is repeated frequently
# 
#------------------------------------------------------------------------------

#Region "Imports"
import traceback
import tempfile
import os
import arcpy
import json

from arcpy import env
from arcpy.sa import *
from arcpy import Describe, Exists,Erase_analysis, FeatureToPolygon_management, GetMessages, EliminatePolygonPart_management

from WiMLib.Config import Config
from WiMLib.SpatialOps import SpatialOps
from WiMLib.Resources import *
from WiMLib import Shared
from WiMLib.MapLayer import *
#End Region

class StreamStatsNationalOps(SpatialOps):
#Region Contructor and Dispose
    def __init__(self, workspacePath):     
        SpatialOps.__init__(self, workspacePath) 
        self.WorkspaceID = os.path.basename(os.path.normpath(workspacePath))
        self.mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
        if not arcpy.Exists(self.mask): raise Exception("Mask does not exist: "+self.mask)
        self._sm("initialized hydroops")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SpatialOps.__exit__(self, exc_type, exc_value, traceback) 
#End region

#Region HydroOps Origin Functions
    def getRasterStatisticHO(self, CharacteristicDef):
        '''
        Calculates the raster statistics using various passed methods
            such as Mean, Median, Mode, Max, and Min.
        HO only notes that it's from HydroOps and keeps it from seeming
            like it is calling itself.
        '''
        ML = None
        result = {CharacteristicDef.Name:None}
        try:
            self._sm("Computing " + CharacteristicDef.Name)
            ML = MapLayer(MapLayerDef(MapLayers[0]))

            arcpy.env.workspace = self._TempLocation
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            result[CharacteristicDef.Name] = self.getRasterStatistic(ML.Dataset, self.mask, CharacteristicDef.Method)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops ReservoirStorage" +tb, "ERROR", 71)
            result[CharacteristicDef.Name] = None

        finally:
            #Cleans up workspace
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
#End Region

#Region AnthOps Origin Functions
    def getStoragePerUnitArea(self, CharacteristicDef):
        '''
        Calculates the Storage per unit area. Is used for computing things
            such as computing the Reservoir storage from National Inventory of Dams (NID)
        '''
        ML = None
        result = {CharacteristicDef.Name:0}
        try:
            self._sm("Computing " + CharacteristicDef.Name)
            ML = MapLayer(MapLayerDef(CharacteristicDef.MapLayers[0]))

            arcpy.env.workspace = self._TempLocation
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            #This calculation should probably be changed depending on what is needed.
            #   I'm guessing this should be a function in Shared.py
            totArea = self.getAreaSqMeter(mask)*Shared.CF_SQMETERS2SQKILOMETER #Put ConversionFactor here?
            #spatial overlay
            #cursor and sum
            with arcpy.da.SearchCursor(self.spatialOverlay(ML.Dataset, mask), ML.QueryField, spatial_reference=ML.spatialreference) as source_curs:
                for row in source_curs:
                    val = WiMLib.Shared.try_parse(row[0], None)
                    result[CharacteristicDef.Name] += float(val)*Shared.CF_ACR2SQKILOMETER/totArea #Put ConversionFactor here?
                #next
            #end with
        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops ReservoirStorage" +tb, "ERROR", 71)
            result[CharacteristicDef.Name] = float('nan')

        finally:
            #Cleans up workspace
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getPercentOfWhole(self, CharacteristicDef): #GREAT EXAMPLE TO REVIEW AND CLEAN UP OTHER SECTIONS!!!
        '''
        Computes the percent of a whole. Useful for calculating percent impervious from the NLCD data,
            percent irrigated agriculture using MIRAD data, and NWALT data.
        '''
        ML = None
        result = {CharacteristicDef.Name:None}
        try:
            self._sm("Computing " + CharacteristicDef.Name)
            ML = MapLayer(MapLayerDef(CharacteristicDef.MapLayer[0]))

            arcpy.env.workspace = self._TempLocation
            if not ML.Activated: 
                raise Exception("Map Layer could not be activated.")

            result[CharacteristicDef.Name] = self.getRasterPercent(ML.Dataset, mask, CharacteristicDef.ClassCodes)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops percentImpervious" +tb, "ERROR", 71)
            result[CharacteristicDef.Name] = None

        finally:
            #Cleans up workspace
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
    def getPointFeatureDensity(self, CharacteristicDef):
        '''
        Computes Major site density. Used when calculating from NPDES.
            Seems like it should be density based on point data, but it is unclear.
        STILL NEEDS WORK - JEREMEY
        '''
        ML = None
        result = {CharacteristicDef.Name:0}
        try:
            self._sm("Computing " + CharacteristicDef.Name)
            ML = MapLayer(MapLayerDef(CharacteristicDef.MapLayers[0]))

            arcpy.env.workspace = self._TempLocation
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            #We could pass "COUNT" at the CharacteristicDef level or here.
            #   As this function is written. Doing something different would
            #   probably result in needing to rename the function.
            tot = self.getFeatureStatistic(ML.Dataset, mask, "COUNT", ML.QueryField)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops ReservoirStorage" +tb, "ERROR", 71)
            result[CharacteristicDef.Name] = float('nan')

        finally:
            #Cleans up workspace
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)

        return result
#End Region