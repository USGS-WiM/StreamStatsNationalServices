#------------------------------------------------------------------------------
#----- FederalHighwayWrapper.py -----------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Wrapper to delineate and compute FederalHighway basin characterisitics.
#
#      usage:  Acts as a wrapper to calcualte the Federal Highway basin
#                   characterisitcs.
#
# discussion:  Intial code was created by Jeremy K. Newson. Some minor edits were done
#                   by John Wall (NC State University).
#
#              See:
#                   https://github.com/GeoJSON-Net/GeoJSON.Net/blob/master/src/GeoJSON.Net/Feature/Feature.cs
#                   http://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/watershed.htm
#                   geojsonToShape: http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/asshape.htm
#
#      dates:   19 AUG 2016 jkn - Created / Date notation edited by jw
#               03 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
import traceback
import datetime
import time
import string
import os
import argparse
import pandas as pd
import arcpy
import gc
from arcpy import env
from arcpy.sa import *
from Ops.HydroOps import  HydroOps
from WIMLib import WiMLogging
from Resources import gage
from Resources import Characteristic
from WIMLib.Resources import Result
from WIMLib import Shared
from WIMLib import GeoJsonHandler
from WIMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
from ServiceAgents.NLDIFileServiceAgent import NLDIFileServiceAgent
from ServiceAgents.NIDServiceAgent import NIDServiceAgent
import ServiceAgents.NLDIServiceAgent
from Ops.StreamStatsNationalOps import StreamStatsNationalOps
import json
from Ops import ExpressionOps

#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
#http://stackoverflow.com/questions/13653991/passing-quotes-in-process-start-arguments
class FederalHighwayWrapper(object):
    #region Constructor
    def __init__(self, workingDirectory, projIdentifier):
        try:
            self.workingDir = workingDirectory        
            self.startTime = time.time()
            self.workspaceID = None
            self._sm("initialized")
            self.globalCatchment = None
            gc.collect()
        except:
            tb = traceback.format_exc()
            self._sm("error running "+tb)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.workingDir = None
        self.startTime= None
        self.workspaceID =None

    def Run(self, gage, parameters, arr=None):
        try:
            #update gage sr
            gage.sr = arcpy.SpatialReference(gage.sr) 
        
            self._sm('-+-+-+-+-+-+-+-+-+ '+ gage.id +' -+-+-+-+-+-+-+-+-+')
            self._sm('-+-+-+-+-+-+-+-+-+ '+ gage.lat +','+ gage.long+' -+-+-+-+-+-+-+-+-+')
            self._sm(' Elapse time:'+ str(round((time.time()- self.startTime)/60, 2))+ 'minutes')
            self._sm('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')

            self.workspaceID = self._delineate(gage,self.workingDir)
            if(self.workspaceID == None): 
                self._sm("Delineation didn't occur for gage "+ gage.id)
                
            basincharacteristics = self._computeCharacteristics(gage,self.workingDir,self.workspaceID,parameters,arr)

            return basincharacteristics
        except:
            tb = traceback.format_exc()
            self._sm("error running "+tb)

    def _delineate(self, gage, workspace):
        try:
            ppoint = arcpy.CreateFeatureclass_management("in_memory", "ppFC"+gage.comid, "POINT", spatial_reference=gage.sr)
            pnt = {"type":"Feature","geometry":{"type":"Point","coordinates":[gage.long,gage.lat]}}
            if (pnt["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(pnt,ppoint,gage.sr)
            else:
                GeoJsonHandler.read_feature_collection(pnt,ppoint,gage.sr)

            if Config()["UseNLDIServices"] == False: #Toggler
                sa = NLDIFileServiceAgent()
            else:
                sa = NLDIServiceAgent()
            maskjson = sa.getBasin(gage.comid, True, gage.long, gage.lat, gage.sr.factoryCode)

            if(not maskjson): return None

            mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
            if (maskjson["type"].lower() =="feature"):
                if not maskjson["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                    raise Exception('Mask Geometry is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature(maskjson,mask,gage.sr)
            else:
                for feature in maskjson["features"]:
                    if not feature["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                        raise Exception('Mask Geometry within the Feature Collection is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature_collection(maskjson,mask,gage.sr) 
#             fileSA = NLDIFileServiceAgent()
            basinjson = sa.getBasin(gage.comid,False)

            if(not basinjson): return None

            self.globalCatchment = arcpy.CreateFeatureclass_management("in_memory", "globalBasin"+gage.comid, "POLYGON", spatial_reference=gage.sr)
            if (basinjson["type"].lower() =="feature"):
                if not basinjson["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                    raise Exception('Basin Geometry is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature(basinjson,self.globalCatchment,gage.sr)
            else:
                for feature in basinjson["features"]:
                    if not feature["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                        raise Exception('Basin Geometry within the Feature Collection is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature_collection(basinjson,self.globalCatchment,gage.sr)
                    
            ssdel = HydroOps(workspace,gage.id)
            ssdel.Delineate(ppoint, mask)
            ssdel.MergeCatchment(self.globalCatchment)

            return ssdel.WorkspaceID
        except:
            tb = traceback.format_exc()
            self._sm("Error delineating basin "+tb)
            return None

    def _computeCharacteristics(self,gage,workspace,workspaceID,parameters,arr):
        method = None
        reportedValues={}
        globalValue ={}

        try:
            WiMResults = Result.Result(gage.comid, "Characteristics computed for "+gage.name)
            with NLDIServiceAgent() as sa:
                globalValue = sa.getBasinCharacteristics(gage.comid)
                globalValue = self.convertUnits(globalValue)
            #end with
            with NIDServiceAgent() as d_sa:
                globalValue['TOT_NID_DISTURBANCE_INDEX'] = d_sa.getDisturbanceIndex(gage.comid)
            #end with

            startTime = time.time()
            with StreamStatsNationalOps(workspace, workspaceID) as sOps:

                #Get basin areas to compute statistics
                localBasinArea = sOps.getAreaSqMeter(sOps.mask)
                globalBasinArea = sOps.getAreaSqMeter(self.globalCatchment)

                for p in parameters:

                    if p == 'TOT_BASIN_AREA':
                        # Get local, global, and total area of basin------------------
                        totalArea = float(globalBasinArea - localBasinArea)
                        varbar = {'totalvalue': totalArea, 'localvalue': localBasinArea,
                                  'globalvalue': globalBasinArea}
                        reportedResults = {'TOT_BASIN_AREA': varbar}
                        WiMResults.Values.update(reportedResults)
                        # ----------------------------------------------------------------
                    else:
                        method = None
                        parameter = Characteristic.Characteristic(p)
                        if(not parameter):
                            self._sm(p +"Not available to compute")
                            continue

                        method = getattr(sOps, parameter.Procedure)

                        if (method):
                            #Initialize result
                            result = None

                            #If multiprocessing array "arr" is not none apply concurrency mechanism
                            #Otherwise process result as normal
                            if arr is not None:
                                proc_char = False
                                while proc_char == False:
                                    arr.acquire()
                                    if p in arr.value:
                                        arr.release()
                                        continue
                                    else:
                                        proc_char = True

                                setattr(arr, 'value', arr.value + ';' + p)

                                arr.release()

                                if parameter.Procedure == 'getCSVStatistic':
                                    result = method(parameter, gage.comid)
                                else:
                                    result = method(parameter)

                                arr.acquire()
                                setattr(arr, 'value', arr.value.replace(';' + p, ''))
                                arr.release()
                            else:
                                if parameter.Procedure == 'getCSVStatistic':
                                    result = method(parameter, gage.comid)
                                else:
                                    result = method(parameter)

                            #todo:merge with request from NLDI
                            self._sm("The local result value for " + str(parameter.Name) + " : " + str(result[parameter.Name]))
                            if(globalValue != None):

                                try:
                                    if parameter.Name not in globalValue:
                                        globalValue[parameter.Name] = self.getTotChar(gage.comid, parameter)
                                    elif globalValue[parameter.Name] == "":
                                        globalValue[parameter.Name] = 0
                                    totalval = ExpressionOps.Evaluate(parameter.AggregationMethod,
                                                                     [float(globalValue[parameter.Name]),float(result[parameter.Name])],
                                                                     [globalBasinArea,localBasinArea]) if globalValue[parameter.Name] != None and result[parameter.Name] != None else None
                                    self._sm("The global value for " + str(parameter.Name) + " : " + str(globalValue[parameter.Name]))
                                    #Below should be updated to work with Total, Local, and Global values
                                    #If the parameter does not exist in globalValue the name is returned screwing things up for calculations
                                    varbar = {'totalvalue':totalval,'localvalue':result[parameter.Name],'globalvalue':globalValue[parameter.Name]}
                                    reportedResults = {parameter.Name:varbar}
                                except:
                                    tb = traceback.format_exc()

                                WiMResults.Values.update(reportedResults) #Tabbed this over - jwx
                            #The following section was put in place by me, John Wall, to help with issues of Global Value = None or where the Parameter is not within a list.
                            #   This was an observed issue after placing the Total, Local, and Global Value component above.
                            #   Looking over the results of including this, we should be able to properly validate our results.
                            #   It should be noted that in at least one instance the WD6190 is not obtained for the Global Value where it is within the CSV.
                            #   Why is this not properly pulled? It's unclear at the current time (8 SEPT 2017)
                            if(globalValue is None or parameter.Name not in globalValue):
                                self._sm("WARNING: Global Value was 'None' or the Parameter was not in the Global Value list!")
                                self._sm("WARNING: Because of the above, Total and Global Values will be 'Not Calculated'.")
                                self._sm("WARNING: Local value should be equal to 'None'!")
                                varbar = {'totalvalue':'Not Calculated','localvalue':result[parameter.Name],'globalvalue':'Not Calculated'}

                                reportedResults = {parameter.Name:varbar}

                                WiMResults.Values.update(reportedResults) #Tabbed this over - jwx

                        else:
                            self._sm(p.Proceedure +" Does not exist","Error")
                            continue

                    #next p
            #end with       
            # print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'
            return WiMResults
        except:
            tb = traceback.format_exc()
            self._sm("Error writing computing Characteristics "+tb)
            return WiMResults

    def getTotChar(self, comId, parameter):

        try:
            idx = int(parameter.TOT_IDX[0])
            df = pd.read_csv(str(parameter.Data), skiprows=1, header=None, sep=',')
            result = df[df[0] == int(comId)][idx].values[0]
            del df
            df = None
        except:
            result = 0

        return result

    def convertUnits(self, globalValues):

        try:
            # Per discussion with Kathy that there was a discrepancy of units in the char
            globalValues['TOT_PPT7100_ANN'] = float(globalValues['TOT_PPT7100_ANN']) * 100
        except:
            print 'Could not convert global value'

        return globalValues

    def _sm(self,msg,type="INFO", errorID=0):        
        WiMLogging.sm(msg,type="INFO", errorID=0)
            


