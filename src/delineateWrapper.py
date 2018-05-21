
#------------------------------------------------------------------------------
#----- DelineateWrapper.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Wrapper to delineate watershed using split catchement methods
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
import os
import argparse
import arcpy
from arcpy import env
from arcpy.sa import *
from Ops.HydroOps import  HydroOps
from WiMLib import WiMLogging
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
            #For project ID
            
            parser.add_argument("-projectID", help="specifies the projectID", type=str, default="ID")
            #Use the following LAT/LON pour point
            parser.add_argument("-pourpoint", help="specifies pourpoint geojson feature ", type=json.loads, 
                                default = '{"type":"Feature","geometry":{"type":"Point","coordinates":[-117.5444,47.7751]}}')
            #Within this EPSG code
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
                           
            args = parser.parse_args()

            startTime = time.time()
            projectID = args.projectID
            if projectID == '#' or not projectID:
                raise Exception('Input Study Area required')
            
            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'))))  
            workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],args.projectID) 
            workspaceID = os.path.basename(os.path.normpath(workingDir))       
            WiMLogging.init(os.path.join(workingDir,"Temp"),"Delineation.log")
            WiMLogging.sm("Started Delineation routine")
            
            sr = arcpy.SpatialReference(args.outwkid)           
            ppoint = arcpy.CreateFeatureclass_management("in_memory", "ppointFC", "POINT", spatial_reference=sr) 
            if (args.pourpoint["type"].lower() =="feature"):
                GeoJsonHandler.read_feature(args.pourpoint,ppoint,sr)
            else:
                GeoJsonHandler.read_feature_collection(args.pourpoint,ppoint,sr)  

            sa = NLDIServiceAgent()
            #to be replaced later by service call etc.
            coords = args.pourpoint['geometry']['coordinates']                                                          #THIS IS WHERE YOU CAHNGE THE COMID
            maskjson = sa.getBasin(None,True,coords[0],coords[1],4326) #Bringing in a JSON mask/catchment ID
            
            if(maskjson):
                comid =maskjson[u'features'][0][u'properties'][u'featureid']
                mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC", "POLYGON", spatial_reference=sr) 
                if (maskjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(maskjson,mask,sr)
                else:
                    GeoJsonHandler.read_feature_collection(maskjson,mask,sr) 
            
            basinjson = sa.getBasin(comid,False)

            if(basinjson):
                basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin", "POLYGON", spatial_reference=sr) 
                if (basinjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(basinjson,basin,sr)
                else:
                    GeoJsonHandler.read_feature_collection(basinjson,basin,sr)         
                    
            hOps = HydroOps(workingDir,workspaceID)
            hOps.Delineate(ppoint, mask)
            hOps.MergeCatchment(basin)
            
            WiMLogging.sm('Finished.  Total time elapsed:', str(round((time.time()- startTime)/60, 2)), 'minutes')

            Results = {
                       "Workspace": hOps.WorkspaceID,
                       "Message": ';'.join(WiMLogging.LogMessages).replace('\n',' ')
                      }
        except:
             tb = traceback.format_exc()
             WiMLogging.sm("Error executing delineation wrapper "+tb)
             Results = {
                       "error": {"message": ';'.join(WiMLogging.LogMessages).replace('\n',' ')}
                       }

        finally:
            print "Results="+json.dumps(Results)

    
if __name__ == '__main__':
    DelineationWrapper()

