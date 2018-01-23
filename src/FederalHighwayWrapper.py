#------------------------------------------------------------------------------
#----- FederalHighwayWrapper.py -----------------------------------------------
#----- Formerly known as DelineateWrapper.py ----------------------------------
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
import arcpy
import gc
from arcpy import env
from arcpy.sa import *
from Ops.HydroOps import  HydroOps
from WiMLib import WiMLogging
from Resources import gage
from Resources import Characteristic
from WiMLib.Resources import Result
from WiMLib import Shared
from WiMLib import GeoJsonHandler
from WiMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
from ServiceAgents.NLDIFileServiceAgent import NLDIFileServiceAgent
import ServiceAgents.NLDIServiceAgent
from Ops.StreamStatsNationalOps import *
import json

#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+
#http://stackoverflow.com/questions/13653991/passing-quotes-in-process-start-arguments
class DelineationWrapper(object):
    #region Constructor
    def __init__(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-projectID", help="specifies the projectID", type=str, default="FH")
            parser.add_argument("-file", help="specifies csv file location including gage lat/long and comid's to estimate", type=str, 
                                default = 'C:\\gis\\gagesiii_lat_lon3.csv')
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "")  
                           
            args = parser.parse_args()
            startTime = time.time()
            projectID = args.projectID
            if projectID == '#' or not projectID:
                raise Exception('Input Study Area required')

            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json')))) 

            if(args.parameters): self.params =  args.parameters.split(";") 
            #get all characteristics from config
            else: self.params =  config["characteristics"].keys() 

            self.workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],args.projectID)   
            header =[]
            header.append("-+-+-+-+-+-+-+-+-+ NEW RUN -+-+-+-+-+-+-+-+-+")
            header.append("Execute Date: " + str(datetime.date.today()))
            header.append("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
                 
            WiMLogging.init(os.path.join(self.workingDir,"Temp"),"gage3.log")
            WiMLogging.sm("Starting routine")
            sr = arcpy.SpatialReference(args.outwkid)             

            file = Shared.readCSVFile(args.file)
            headers = file[0]
            if "gage_no_1" in headers: idindex = headers.index("gage_no_1")
            if "gage_name" in headers: nmindex = headers.index("gage_name")
            if "COMID" in headers: comIDindex = headers.index("COMID")
            if "lat" in headers: latindex = headers.index("lat")
            if "lon" in headers: longindex = headers.index("lon")

            #remove header
            file.pop(0)
            Shared.writeToFile(os.path.join(self.workingDir,config["outputFile"]),header)
            isFirst = True
            for station in file:
                g = gage.gage(station[idindex],station[comIDindex],station[latindex],station[longindex],sr,station[nmindex])

                WiMLogging.sm('-+-+-+-+-+-+-+-+-+ '+ g.comid +' -+-+-+-+-+-+-+-+-+')
                WiMLogging.sm('-+-+-+-+-+-+-+-+-+ '+ g.lat +','+ g.long+' -+-+-+-+-+-+-+-+-+')
                WiMLogging.sm(' Elapse time:'+ str(round((time.time()- startTime)/60, 2))+ 'minutes')
                WiMLogging.sm('-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+')

                workspaceID = self._delineate(g,self.workingDir)
                if(workspaceID == None): 
                    WiMLogging.sm("Delineation didn't occur for gage "+ g.comid)
                    continue
                results = self._computeCharacteristics(g,self.workingDir,workspaceID)

                #Put for-for k.subk routine here instead of below
                complexHeader = []
                allValues = []
                for k in results.Values.keys():
                    for subk in ['localvalue','totalvalue','globalvalue']:
                        complexHeader.append(str(k) + "_" + str(subk))
                        allValues.append(results.Values[k][subk])

                #write results to file
                #Below should probably be expanded upon
                if isFirst:
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(['COMID','WorkspaceID','Description','LAT','LONG']+complexHeader))
                    isFirst = False
                if results is None: #changed to elif by jwx
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,workspaceID,'error',g.lat,g.long])) 
                else:
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,workspaceID,results.Description,g.lat,g.long]+allValues))                        
                del complexHeader
                del allValues
                gc.collect()
            #next station           

            print 'Finished.  Total time elapsed:', round((time.time()- startTime)/60, 2), 'minutes'

        except:
            tb = traceback.format_exc()
            WiMLogging.sm("error running "+tb)

    def _delineate(self, gage, workspace):
        try:
            ppoint = arcpy.CreateFeatureclass_management("in_memory", "ppFC"+gage.comid, "POINT", spatial_reference=gage.sr)
            pnt = {"type":"Feature","geometry":{"type":"Point","coordinates":[gage.lat,gage.long]}}
            if (pnt["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(pnt,ppoint,gage.sr)
            else:
                GeoJsonHandler.read_feature_collection(pnt,ppoint,gage.sr)  

            if Config()["UseNLDIServices"] == False: #Toggler
                sa = NLDIFileServiceAgent()
            else:
                sa = NLDIServiceAgent()
            maskjson = sa.getBasin(gage.comid, True, gage.lat, gage.long, gage.sr.factoryCode)

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

            basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
            if (basinjson["type"].lower() =="feature"):
                if not basinjson["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                    raise Exception('Basin Geometry is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature(basinjson,basin,gage.sr)
            else:
                for feature in basinjson["features"]:
                    if not feature["geometry"]["type"].lower() in ["polygon","multipolygon"]:
                        raise Exception('Basin Geometry within the Feature Collection is not polygon output will be erroneous!')
                GeoJsonHandler.read_feature_collection(basinjson,basin,gage.sr)         
                    
            ssdel = HydroOps(workspace,gage.comid)
            ssdel.Delineate(ppoint, mask)
            ssdel.MergeCatchment(basin)

            return ssdel.WorkspaceID
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error delineating basin "+tb)
            return None
    def _computeCharacteristics(self,gage,workspace,workspaceID):
        method = None
        reportedValues={}
        try:
            WiMResults = Result.Result(gage.comid,"Characteristics computed for "+gage.name)
            with NLDIServiceAgent() as sa:
                globalValue = sa.getBasinCharacteristics(gage.comid)
            #end with
            startTime = time.time()
            with StreamStatsNationalOps(workspace, workspaceID) as sOps: 
                for p in self.params:
                    if p == 'TOT_BASIN_AREA':
                        print "TOT_BASIN_AREA hath been found!"
                    method = None
                    parameter = Characteristic.Characteristic(p)
                    if(not parameter): 
                        WiMLogging.sm(p +"Not available to compute")
                        continue

                    method = getattr(sOps, parameter.Procedure)
                    print "The parameter name is: " + parameter.Name
                    #if method != 'getPrismStatistic':
                    #    continue
                    if (method): 
                        result = method(parameter) 
                        #todo:merge with request from NLDI
                        WiMLogging.sm("The local result value for " + str(parameter.Name) + " : " + str(result[parameter.Name]))
                        if(globalValue != None and parameter.Name in globalValue): 
                            print "The Name is: " + parameter.Name
                            try:
                                if globalValue[parameter.Name] == "":
                                    globalValue[parameter.Name] = 0                              
                                totalval = float(globalValue[parameter.Name])-float(result[parameter.Name]) if globalValue[parameter.Name] != None and result[parameter.Name] != None else None
                                WiMLogging.sm("The global value for " + str(parameter.Name) + " : " + str(globalValue[parameter.Name]))
                                #Below should be updated to work with Total, Local, and Global values
                                #If the parameter does not exist in globalValue the name is returned screwing things up for calculations
                                varbar = {'totalvalue':totalval,'localvalue':result[parameter.Name],'globalvalue':globalValue[parameter.Name]}
                                reportedResults = {parameter.Name:varbar}
                            except:
                                "Couldn't convert " + parameter.Name + " to Float"

                            WiMResults.Values.update(reportedResults) #Tabbed this over - jwx
                        #The following section was put in place by me, John Wall, to help with issues of Global Value = None or where the Parameter is not within a list.
                        #   This was an observed issue after placing the Total, Local, and Global Value component above.
                        #   Looking over the results of including this, we should be able to properly validate our results.
                        #   It should be noted that in at least one instance the WD6190 is not obtained for the Global Value where it is within the CSV.
                        #   Why is this not properly pulled? It's unclear at the current time (8 SEPT 2017)
                        if(globalValue is None or parameter.Name not in globalValue):
                            WiMLogging.sm("WARNING: Global Value was 'None' or the Parameter was not in the Global Value list!")
                            WiMLogging.sm("WARNING: Because of the above, Total and Global Values will be 'Not Calculated'.")
                            WiMLogging.sm("WARNING: Local value should be equal to 'None'!")
                            varbar = {'totalvalue':'Not Calculated','localvalue':result[parameter.Name],'globalvalue':'Not Calculated'}

                            reportedResults = {parameter.Name:varbar}

                            WiMResults.Values.update(reportedResults) #Tabbed this over - jwx

                    else:
                        WiMLogging.sm(p.Proceedure +" Does not exist","Error")
                        continue 

                #next p
            #end with       
            print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'

            return WiMResults
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error writing computing Characteristics "+tb)
            return WiMResults
            
if __name__ == '__main__':
    DelineationWrapper()


