
#------------------------------------------------------------------------------
#----- DelineateWrapper.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2017 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Wrapper to delineate and compute FederalHighway basin char 
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
import time
import string
import os
import argparse
import arcpy
from arcpy import env
from arcpy.sa import *
from Ops.HydroOps import  HydroOps
from WiMLib import WiMLogging
from Resources import gage
from WiMLib import Shared
from WiMLib import GeoJsonHandler
from WiMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
import ServiceAgents.NLDIServiceAgent
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
                                default = 'D:\\ss_apps\\gages_iii\\Unique_CONUS_Gages (2).csv')
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
                           
            args = parser.parse_args()
            startTime = time.time()
            projectID = args.projectID
            if projectID == '#' or not projectID:
                raise Exception('Input Study Area required')

            config = Config(json.load(open('./config.json')))  
            workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],args.projectID)   
            header =[]
            header.append("-+-+-+-+-+-+-+-+-+ NEW RUN -+-+-+-+-+-+-+-+-+")
            header.append("Execute Date: " + str(datetime.date.today()))
            header.append("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
                 
            WiMLogging.init(os.path.join(workingDir,"Temp"),"Delineation.log")
            WiMLogging.sm("Starting routine")
            sr = arcpy.SpatialReference(args.outwkid)             

            file = self._readCSVFile(args.file)
            headers = file[0]
            if "gage_no_1" in headers: idindex = headers.index("gage_no_1")
            if "gage_name" in headers: nmindex = headers.index("gage_name")
            if "COMID" in headers: comIDindex = headers.index("COMID")
            if "lat" in headers: latindex = headers.index("lat")
            if "long" in headers: longindex = headers.index("long")

            #remove header
            file.pop(0)
            self._writeToFile(os.path.join(workingDir,config["outputFile"]),header)
            isFirst = True
            for station in file:
                g = gage.gage(station[idindex],station[comIDindex],station[latindex],station[longindex],sr,station[nmindex])
                workspaceID = self._delineate(g,workingDir)
                results = self._computeCharacteristics(g,workingDir,workspaceID)

                #write results to file
                if isFirst:
                    self._appendLineToFile(os.path.join(workingDir,config["outputFile"]),",".join(["header1","header2","header3"]))
                    isFirst = False
                self._appendLineToFile(os.path.join(workingDir,config["outputFile"]),",".join(["result1","result2","result3"]))
            #next station           
            
            print 'Finished.  Total time elapsed:', round((time.time()- startTime)/60, 2), 'minutes'

        except:
             tb = traceback.format_exc()
             WiMLogging.sm("error running "+tb)

    def _delineate(self, gage, workspace):
            ppoint = arcpy.CreateFeatureclass_management("in_memory", "ppointFC", "POINT", spatial_reference=gage.sr)
            pnt = {"type":"Feature","geometry":{"type":"Point","coordinates":[gage.lat,gage.long]}} 
            if (pnt["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(pnt,ppoint,gage.sr)
            else:
                GeoJsonHandler.read_feature_collection(pnt,ppoint,gage.sr)  

            sa = NLDIServiceAgent()
            maskjson = sa.getBasin(gage.comid,True)

            if(maskjson):
                mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC", "POLYGON", spatial_reference=gage.sr) 
                if (maskjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(maskjson,mask,gage.sr)
                else:
                    GeoJsonHandler.read_feature_collection(maskjson,mask,gage.sr) 
            
            basinjson = sa.getBasin(gage.comid,False)

            if(basinjson):
                basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin"+gage.comid, "POLYGON", spatial_reference=sr) 
                if (basinjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(basinjson,basin,sr)
                else:
                    GeoJsonHandler.read_feature_collection(basinjson,basin,sr)         
                    
            ssdel = HydroOps(workspace)
            ssdel.Delineate(ppoint, mask)
            ssdel.MergeCatchment(basin)

            return ssdel.WorkspaceID
    def _computeCharacteristics(self,gage,workspace,workspaceID):
        method = None
        try:
            WiMResults = Result.Result("Characteristics computed for "+workspaceID)
            workingDir = os.path.join(workspace,workspaceID)
            startTime = time.time()
            with StreamStatsNationalOps(self.workingDir) as sOps: 
                for p in self.params:
                    method = None
                    parameter = Characteristic.Characteristic(p)
                    if(not parameter): 
                        self._sm(p +"Not available to compute")
                        continue

                    method = getattr(sOps, parameter.Procedure) 
                    if (method): 
                        WiMResults.Values.update(method(parameter))  
                        #todo:merge with request from NLDI
                    else:
                        self._sm(p.Proceedure +" Does not exist","Error")
                        continue   
                            
                #next p
            #end with       
            print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'

            return WiMResults
        except:
             tb = traceback.format_exc()
             
    def _readCSVFile(self, file):
        f = None
        try:
            if (not os.path.isfile(file)):
                self.__sm__(file +" does not exist. If this is an error, check path.", 0.178)
                return []
            f = open(file, 'r')
            return map(lambda s: s.strip().split(","), f.readlines())
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error reading csv file "+tb)
        finally:
            if not f == None:
                if not f.closed :
                    f.close();
    def _appendLineToFile(self, file, content):
        f = None
        try:
            f = open(file, "a")            
            f.write(string.lower(content + '\n'))
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error appending line to file "+tb)

        finally:
            if not f == None or not f.closed :
                f.close();
    def _writeToFile(self, file, content):
        f = None
        try:
            f = open(file, "w")
            f.writelines(map(lambda x:x+'\n', content))
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error writing to file "+tb)
        finally:
            if not f == None or not f.closed :
                f.close();
    
if __name__ == '__main__':
    DelineationWrapper()

