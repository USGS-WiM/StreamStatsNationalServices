
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
from Resources import Characteristic
from WiMLib.Resources import Result
from WiMLib import Shared
from WiMLib import GeoJsonHandler
from WiMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
import ServiceAgents.NLDIServiceAgent
from Ops.StreamStatsNationalOps import *
import json
#INFO 0 -+-+-+-+-+-+-+-+-+ 4287975 -+-+-+-+-+-+-+-+-+
#INFO 0 -+-+-+-+-+-+-+-+-+ -68.58527778,47.2833333 -+-+-+-+-+-+-+-+-+
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
                                default = 'D:\\ss_apps\\ss_apps\\gages_iii\\gagesiii_lat_lon.csv')
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "TOT_PPT7100_FEB")  
                           
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

                #write results to file
                if isFirst:
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(['COMID','WorkspaceID','Description','LAT','LONG']+results.Values.keys()))
                    isFirst = False
                
                if results is None:
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,workspaceID,'error',g.lat,g.long])) 
                else:
                    Shared.appendLineToFile(os.path.join(self.workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,workspaceID,results.Description,g.lat,g.long]+results.Values.values()))             
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

            sa = NLDIServiceAgent()
            maskjson = sa.getBasin(gage.comid,True)

            if(not maskjson): return None

            mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
            if (maskjson["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(maskjson,mask,gage.sr)
            else:
                GeoJsonHandler.read_feature_collection(maskjson,mask,gage.sr) 
            
            basinjson = sa.getBasin(gage.comid,False)

            if(not basinjson): return None

            basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
            if (basinjson["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(basinjson,basin,gage.sr)
            else:
                GeoJsonHandler.read_feature_collection(basinjson,basin,gage.sr)         
                    
            ssdel = HydroOps(workspace,gage.comid)
            ssdel.Delineate(ppoint, mask)
            ssdel.MergeCatchment(basin)

            return ssdel.WorkspaceID
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error writing computing Characteristics "+tb)
            return None
    def _computeCharacteristics(self,gage,workspace,workspaceID):
        method = None
        try:
            WiMResults = Result.Result(gage.comid,"Characteristics computed for "+gage.name)
            with NLDIServiceAgent() as sa:
                globalValue = sa.getBasinCharacteristics(gage.comid)
            #end with
            startTime = time.time()
            with StreamStatsNationalOps(workspace, workspaceID) as sOps: 
                for p in self.params:
                    method = None
                    parameter = Characteristic.Characteristic(p)
                    if(not parameter): 
                        self._sm(p +"Not available to compute")
                        continue

                    method = getattr(sOps, parameter.Procedure) 
                    if (method): 
                        result = method(parameter) 
                        #todo:merge with request from NLDI
                        if(parameter.Name in globalValue): 
                            result[parameter.Name] = float(globalValue[parameter.Name])-result[parameter.Name]

                        WiMResults.Values.update(result)
                    else:
                        self._sm(p.Proceedure +" Does not exist","Error")
                        continue 

                #next p
            #end with       
            print 'Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes'

            return WiMResults
        except:
             tb = traceback.format_exc()
             WiMLogging.sm("Error writing computing Characteristics "+tb)
    
if __name__ == '__main__':
    DelineationWrapper()

