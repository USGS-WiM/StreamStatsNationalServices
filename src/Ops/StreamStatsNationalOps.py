#------------------------------------------------------------------------------
#----- StreamStatsNationalOps.py ----------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
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
#               11 APR 2017 jw - Added getVectoryDensity
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
#------------------------------------------------------------------------------

#Region "Imports"
import traceback
import tempfile
import os
import arcpy
import json
import math
from datetime import datetime as dt
import pandas as pd
import numpy as np
from arcpy import env
from arcpy.sa import *
from arcpy import Describe, Exists,Erase_analysis, FeatureToPolygon_management, GetMessages, EliminatePolygonPart_management

from WiMLib.Config import Config
from WiMLib.SpatialOps import SpatialOps
from WiMLib.Resources import *
from WiMLib import Shared
from WiMLib.MapLayer import *
from Assets.Calculator import calculate
from Resources import Characteristic as configChar
#End Region

class StreamStatsNationalOps(SpatialOps):
#Region Contructor and Dispose
    def __init__(self, workspacePath, workspaceID):     
        super(StreamStatsNationalOps,self).__init__(workspacePath) 
        self.WorkspaceID = workspaceID
        self.mask = os.path.join(os.path.join(self._WorkspaceDirectory, self.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["downstream"])
        if not arcpy.Exists(self.mask): raise Exception("Mask does not exist: "+self.mask)
        self._sm("initialized StreamStatsNationalOps")
        arcpy.ResetEnvironments()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        super(StreamStatsNationalOps,self).__exit__(exc_type, exc_value, traceback) 
#End region
    def getRasterStatistic(self, Characteristic):
        '''
        Calculates the raster statistics using various passed methods
            such as Mean, Median, Mode, Max, and Min.
        '''
        ML = None
        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)
#            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]), "", self.mask)
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            result[Characteristic.Name] = super(StreamStatsNationalOps,self).getRasterStatistic(ML.Dataset, self.mask, Characteristic.Method)*Characteristic.MultiplicationFactor

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("getRasterStatistic error" +tb +" "+Characteristic.Name, "ERROR", 71)
            result[Characteristic.Name] = None

        finally:
            #Cleans up workspace
            ML = None

        return result
#Region Methods
    def getFeatureStatistic(self, Characteristic):
        '''
        Computes feature stat.
        '''
        ML = None
        result = {Characteristic.Name:0}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))

            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            tot = super(StreamStatsNationalOps,self).getFeatureStatistic(ML.Dataset, self.mask, Characteristic.Method, Characteristic.QueryField, Characteristic.WhereClause)

            result[Characteristic.Name] = tot[Characteristic.QueryField][Characteristic.Method]

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("getPointFeatureDensity "+ Characteristic.Name+" " +tb, "ERROR", 71)
            result[Characteristic.Name] = float('nan')

        finally:
            #Cleans up workspace
            ML = None

        return result
    def getStoragePerUnitArea(self, Characteristic):
        '''
        Calculates the Storage per unit area. Is used for computing things
            such as computing the Reservoir storage from National Inventory of Dams (NID)
        '''
        ML = None
        result = {Characteristic.Name:0}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            ML_sr = arcpy.Describe(ML.Dataset).spatialReference

            arcpy.env.workspace = self._TempLocation
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            #This calculation should probably be changed depending on what is needed.
            #   I'm guessing this should be a function in Shared.py
            totArea = self.getAreaSqMeter(self.mask)*Shared.CF_SQMETERS2SQKILOMETER #Put ConversionFactor here?
            #spatial overlay
            #cursor and sum
            with arcpy.da.SearchCursor(self.spatialOverlay(ML.Dataset, self.mask), Characteristic.QueryField, spatial_reference=ML_sr) as source_curs:
                for row in source_curs:
                    val = WiMLib.Shared.try_parse(row[0], None)
                    result[Characteristic.Name] += float(val)*Shared.CF_ACR2SQKILOMETER/totArea #Put ConversionFactor here?
                #next
            #end with
        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("ReservoirStorage" +tb, "ERROR", 71)
            result[Characteristic.Name] = float('nan')

        finally:
            #Cleans up workspace
            ML = None

        return result
    def getRasterPercent(self, Characteristic):
        '''
        Computes the percent of a whole. Useful for calculating percent impervious from the NLCD data,
            percent irrigated agriculture using MIRAD data, and NWALT data.
        '''
        ML = None
        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            if not ML.Activated: 
                raise Exception("Map Layer could not be activated.")

            result[Characteristic.Name] = super(StreamStatsNationalOps,self).getRasterPercent(ML.Dataset, self.mask, Characteristic.ClassCodes)*Characteristic.MultiplicationFactor

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops percentImpervious" +tb, "ERROR", 71)
            result[Characteristic.Name] = None

        finally:
            #Cleans up workspace
            ML = None

        return result
#     def getRasterStatistic(self, Characteristic):
#         '''
#         Computes the percent of a whole. Useful for calculating percent impervious from the NLCD data,
#             percent irrigated agriculture using MIRAD data, and NWALT data.
#         '''
#         ML = None
#         result = {Characteristic.Name:None}
#         try:
#             self._sm("Computing " + Characteristic.Name)
#             ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
#             if not ML.Activated: 
#                 raise Exception("Map Layer could not be activated.")
# 
#             result[Characteristic.Name] = super(StreamStatsNationalOps,self).getRasterStatistic(ML.Dataset, self.mask, Characteristic.Method)
# 
#         except:
#             tb = traceback.format_exc()
#             self._sm(arcpy.GetMessages(), 'GP')
#             self._sm("Error getRasterStatistic " + Characteristic.Name+ " " +tb, "ERROR", 71)
#             result[Characteristic.Name] = None
# 
#         finally:
#             #Cleans up workspace
#             ML = None
# 
#         return result
    def getPointFeatureDensity(self, Characteristic):
        '''
        Computes feature count per unit area.
        '''
        ML = None
        result = {Characteristic.Name:0}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))

            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            totArea = self.getAreaSqMeter(self.mask)*Shared.CF_SQMETERS2SQKILOMETER
            count = super(StreamStatsNationalOps,self).getFeatureCount(ML.Dataset, self.mask)

            result[Characteristic.Name] = count/totArea

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("getPointFeatureDensity "+ Characteristic.Name+" " +tb, "ERROR", 71)
            result[Characteristic.Name] = float('nan')

        finally:
            #Cleans up workspace
            ML = None

        return result

    def getVectorDensity(self, Characteristic):
        '''
        Is a modification of getPointFeatureDensity. Initially created to calculate the percent of dams per stream.
        This method is a mash-up of prior work done within this method and the getFeatureStatistic Method found in SpatialOps.py.
        Mashed-up by JWX.
        '''

        map = []
        analysisFeatures = []
        ML = None
        result = {Characteristic.Name:0}
        try:
            self._sm("Computing " + Characteristic.Name)

            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]), "", self.mask)

            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")

            spOverlayWhole = self.spatialOverlay(ML.Dataset, self.mask, "INTERSECTS")               #Added back after sumMain was removed
            analysisFeatures.append(spOverlayWhole[0])

            #Create query
            queryField =  "{}".format(Characteristic.Field)                                         #Generalized to pass whatever field needed
            operator = Characteristic.Operator                                                      #Generalized to whatever operator e.g. =, LIKE, !=
            if operator == "LIKE":                                                                  #If operator = LIKE, flanking "%" are needed
                keyword = "'%{}%'".format(Characteristic.Keyword)
            else:
                keyword = Characteristic.Keyword
            query = "{} {} {}".format(queryField,operator,keyword)                                  #Build query

            #Create sub-set feature class using query
            arcpy.MakeFeatureLayer_management(spOverlayWhole, "Subsetlayer")                        #Make feature layer
            arcpy.SelectLayerByAttribute_management("Subsetlayer", "NEW_SELECTION", query)          #Carry out selection
            outName = os.path.join(self._TempLocation, "vdtmp.shp")                                 #SHP has to be included for proper function
            arcpy.CopyFeatures_management("Subsetlayer", outName)                                   #Copy out features to avoid selection errors
            arcpy.SelectLayerByAttribute_management("Subsetlayer", "CLEAR_SELECTION")
            if arcpy.GetCount_management(outName).getOutput(0) == "0":                              #Catch if the dataset is blank
                self._sm("Warning: Subset feature is blank. Zero will be substituded.")
                result[Characteristic.Name] = 0                                                     #If blank, result is zero
            else:
                analysisFeatures.append(outName)

            #Get methods and field for analysis
            statisticRules = Characteristic.Method
            Fields = Characteristic.MethField                                                        #Method operation field (newly added to config.json)
            #methods = [x.strip() for x in statisticRules.split(';')]                                #Could be used to scale the method section
            #Fields = [x.strip() for x in fieldStr.split(';')]                                       #Could be used to scale the fields section
            map.append([Fields,statisticRules])                                                      #Build statistics statement

            for feaure in analysisFeatures:                                                          #NEEDED CALCULATE EVERYTHING***
                resultCalculation = []                                                               #AN ARRAY TO CAPTURE VALUES***
                tblevalue = arcpy.Statistics_analysis(feaure,os.path.join(self._TempLocation, "aftmp"),map)
                mappedFeilds = [x[1]+"_"+x[0] for x in map]
                cursor = arcpy.da.SearchCursor(tblevalue, mappedFeilds)
                for row in cursor:
                    resultCalculation.append(row)

            #Generate values for results
            if len(analysisFeatures) == 1:                                                            #Catch streams only instances
                result[Characteristic.Name] = 0
            else:
                if resultCalculation[0] == 0:                                                         #Catch canal only instances
                    result[Characteristic.Name] = 100
                else:
                    result[Characteristic.Name] = (resultCalculation[1]/resultCalculation[0])*100     #Otherwise carry out math

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("getVectorDensity "+ Characteristic.Name+" " +tb, "ERROR", 71)
            result[Characteristic.Name] = float('nan')

        finally:
            #Cleans up workspace
            ML = None
            arcpy.SelectLayerByAttribute_management("Subsetlayer", "CLEAR_SELECTION")                 #This was added by JWX

        return result

    def getCalculateEval(self, Characteristic):
        """
            This method takes input from config.json including: Variables, Equation, EquationVariables, MapLayers, and SubProcedure.
            The initial component of this method calcualtes the subprocedure(s) on each maplayer and returns the variable. For example,
            if a given input has Variables "TOT_TMIN7100" and "TOT_TMAX7100", MapLayers "tmin7100_800a" and "tmax7100_800a", and
            SubProcedure "getPrismStatistic", then the intial component should calcualte the getPrismStatistic method using MapLayers
            "tmin7100_800a" and "tmax7100_800a". The Variables component is not entirely needed and could probably be disposed.

            The second component takes the input equation and equation variables from config.json and replaces the equation variables
            with the results from the first component of this method. Finally, eval() is invoked to calculate the result.

            N.B.: As of 31 MAY 2017 this method is a rough draft by JWX and should be cleaned up.
        """
        result = {Characteristic.Name:None}
        try:
            variableValues = []
            for p in Characteristic.Variables:                              #For each Variable
                method = None
                parameter = Characteristic.SubProcedure                 #Use the defined SubProcedure
                method = getattr(self, parameter) 
                characteristic = configChar.Characteristic(p)
                val = method(characteristic)                          #Return value for self.procedure
                variableValues.append(val)                               #Update MY array with returned value
                
            vals = []
            for x in variableValues:
                vals.append(float(x.values()[0]))
                
                
            result[Characteristic.Name] = calculate(str(Characteristic.Equation).format(*vals))                           #Obtain equation from config.json                             #Evaluate the results
        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("To be determined error" +tb +" "+Characteristic.Name, "ERROR", 71)
            result[Characteristic.Name] = None

        return result

    def toBeDetermined(self, Characteristic):

        #Is a place holder characteristic. Is stripped down version of getPrismStatistic. Created by JWX.

        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)

            result[Characteristic.Name] = "To be determined"

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("To be determined error" +tb +" "+Characteristic.Name, "ERROR", 71)
            result[Characteristic.Name] = None

            #Not much to be cleaned up

        return result

    def getPrismStatistic(self, Characteristic):

        #Computes statistic for prism data. Changed by JWX. Indent block did not work.


        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            
            if not ML.Activated:
                raise Exception("Map Layer could not be activated.")
           
            
            timeRange = [dt.strptime(str(x), '%m-%d-%Y') for x in Characteristic.TimeRange.split(';')] 
            
            result[Characteristic.Name] = super(StreamStatsNationalOps,self).getPrismStatistic(
                ML.Dataset,self.mask, Characteristic.Method, timeRange, 
                Characteristic.TimeMethod, Characteristic.Data)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("getPrismStatistic error" +tb +" "+Characteristic.Name, "ERROR", 71)
            result[Characteristic.Name] = None

        finally:
            #Cleans up workspace
            ML = None

        return result

    def NHDPlusV2QueryNoCalc(self, Characteristic):
        '''
        This method returns a zero value. This is used when NHD Plus version 2 is noted in the metadata for the characteristic.
            The resulting Total Value is therefore the Global value since the total is calcualted as Global less Local.
        
        Original outline for this code was pulled from getRasterPercent.
        '''
        ML = None
        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            if not ML.Activated: 
                raise Exception("Map Layer could not be activated.")

            result[Characteristic.Name] = 0

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops percentImpervious" +tb, "ERROR", 71)
            result[Characteristic.Name] = None

        finally:
            #Cleans up workspace
            ML = None

        return result

    def getLogRasterStatistic(self, Characteristic):
        '''
        This method returns a the natural log of values returned from Raster Statistic. This is only used for TWI at the moment.
        
        Original outline for this code was pulled from getPointFeatureDensity.
        '''
        ML = None
        result = {Characteristic.Name:None}
        try:
            self._sm("Computing " + Characteristic.Name)
            ML = MapLayer(MapLayerDef(Characteristic.MapLayers[0]))
            if not ML.Activated: 
                raise Exception("Map Layer could not be activated.")

            rastStat = super(StreamStatsNationalOps,self).getRasterStatistic(ML.Dataset, self.mask,"MEAN")

            result[Characteristic.Name] = np.log(rastStat)

        except:
            tb = traceback.format_exc()
            self._sm(arcpy.GetMessages(), 'GP')
            self._sm("Anthops percentImpervious" +tb, "ERROR", 71)
            result[Characteristic.Name] = None

        finally:
            #Cleans up workspace
            ML = None

        return result
    
    def getCSVStatistic(self, Characteristic):
        '''
        This method looks in the conus text file and returns the NA statistic
        '''
        
        result = {Characteristic.Name:None}
        df = pd.read_csv(str(Characteristic.Data), skiprows=1, header=None, sep=',')
        idx = int(Characteristic.IDX)
        
        try:
            result[Characteristic.Name] = df[df[0] == int(Characteristic.ComID)][idx].values[0]
        except:
            result[Characteristic.Name] = None

        del df
        df = None
        
        return result
#End Region