
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
import os
from arcpy import Describe, Exists,Erase_analysis,FeatureToPolygon_management,GetMessages,EliminatePolygonPart_management
from arcpy import env
from arcpy.sa import *
import json
from  WiMLib.SpatialOps import SpatialOps
from WiMLib.MapLayer import *
from WiMLib.Config import Config
#endregion

class HydroOps(SpatialOps):
    #region Constructor and Dispose
    def __init__(self, workspacePath, id):     
        SpatialOps.__init__(self, workspacePath) 
        self.WorkspaceID = id

        self._sm("initialized hydroops")

        arcpy.ResetEnvironments()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SpatialOps.__exit__(self, exc_type, exc_value, traceback) 
    #endregion   
        
    #region Methods   
    def Delineate(self, PourPoint, inmask = None):
        #http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/watershed.htm
        fdr = None
        sr = None
        mask = None
        datasetPath = None
        featurePath = None
        outWatershedRaster = None
        upCatch = None
        dstemp = None
        downCatch = None
        try:
            catchments = Config()["catchment"]
            arcpy.env.workspace = self._TempLocation
            self._sm("Delineating catchment")
            fdr = MapLayer(MapLayerDef("fdr"), "", PourPoint)

            if not fdr.Activated:
                raise Exception("Flow direction could not be activated.")

            fac = MapLayer(MapLayerDef("fac"), fdr.TileID)

            if not fac.Activated:
                raise Exception("Flow accumulation could not be activated.")

            sr = fdr.spatialreference
            if inmask != None:
                mask = self.ProjectFeature(inmask, sr)

            datasetPath = arcpy.CreateFileGDB_management(self._WorkspaceDirectory, self.WorkspaceID +'.gdb')[0]
            featurePath = arcpy.CreateFeatureDataset_management(datasetPath, 'Layers', sr )[0]

            self._sm("creating workspace environment. "+ datasetPath)
            arcpy.CheckOutExtension("Spatial")
            self._sm("Starting Delineation")
            arcpy.env.extent = arcpy.Describe(mask).extent

            outSnapPour = SnapPourPoint(PourPoint, fac.Dataset, 60)

            #arcpy.env.extent = arcpy.Describe(mask).extent

            outWatershedRaster = Watershed(fdr.Dataset, outSnapPour)
            #arcpy.env.extent = "MAXOF"

            upCatch = os.path.join(featurePath, catchments["upstream"])
            arcpy.RasterToPolygon_conversion(outWatershedRaster, upCatch, "NO_SIMPLIFY")
            #strip downstream catchment from mask
            dstemp = arcpy.Erase_analysis(mask, upCatch, "dstemp")
            downCatch = self.__removePolygonHoles(dstemp, featurePath, catchments["downstream"])
            self._sm(arcpy.GetMessages(), 'AHMSG')
            self._sm("Finished")
        except:
            tb = traceback.format_exc()
            self._sm("Delineation Error "+tb, "ERROR")

        finally:
            arcpy.CheckInExtension("Spatial")
            #Local cleanup
            if fdr != None: del fdr
            if sr != None: del sr
            if mask != None: arcpy.Delete_management(mask)
            if dstemp != None: arcpy.Delete_management(dstemp); dstemp = None
            for raster in arcpy.ListRasters("*", "GRID"):
                arcpy.Delete_management(raster)
            if datasetPath != None: del datasetPath
            if featurePath != None: del featurePath
            if upCatch != None: del upCatch; upCatch = None
            if downCatch != None: del downCatch; downCatch = None
            arcpy.env.extent = ""
    def MergeCatchment(self,inbasin):
        dstemp = None
        try:
            catchments = Config()["catchment"]
            env.workspace = self._TempLocation
            resultworkspace = os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers")
            downstreamcatchment = os.path.join(resultworkspace, catchments["downstream"])
            dsDesc = Describe(downstreamcatchment)
            if not Exists(downstreamcatchment): raise Exception("downstream catchment doesn't exist")
            sr = dsDesc.spatialReference

            wrkingbasin = self.ProjectFeature(inbasin, sr)

            #strip downstream catchment from mask
            dstemp = Erase_analysis(wrkingbasin, downstreamcatchment, "dstemp")
            #remove any weird verticies associated with Erase
            globalbasin = os.path.join(resultworkspace, catchments["global"])
            FeatureToPolygon_management(dstemp, globalbasin, cluster_tolerance="50 Meters", attributes="ATTRIBUTES", label_features="")

            if not Exists(globalbasin): raise Exception("Failed to create basin " + GetMessages())
            return True
        except:
            tb = traceback.format_exc()
            self._sm("Merge basin Error "+tb, "ERROR")
            return False
        finally:
            #cleanup
            for fs in arcpy.ListFeatureClasses():
                arcpy.Delete_management(fs)
            for rs in arcpy.ListRasters():
                arcpy.Delete_management(rs)
    #endregion

    #region Helper Methods
    def __removePolygonHoles(self, polyFC, path, featurename):
        try:
            result = EliminatePolygonPart_management(polyFC, os.path.join(path, featurename), condition="PERCENT", 
                                                    part_area="0 SquareMeters", part_area_percent="5", part_option="ANY")
            self._sm(arcpy.GetMessages())
            return result
        except:
            tb = traceback.format_exc()
            self._sm("Error removing holes "+tb, "ERROR")
            return polyFC
    def __getDirectory(self, subDirectory, makeTemp=True):
        try:
            if os.path.exists(subDirectory):
                shutil.rmtree(subDirectory)
            os.makedirs(subDirectory)

            #temp dir
            if makeTemp:
                os.makedirs(os.path.join(subDirectory, "Temp"))

            return subDirectory
        except:
            x = GetMessages()
            return subDirectory
    #endregion