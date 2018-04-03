
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
import fnmatch
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
        nidFC = None
        try:
            parser = argparse.ArgumentParser()
            #Use the following LAT/LON pour point
            parser.add_argument("-dataset", help="datasetpath", type=str, 
                                default = 'D:\data\USGS_Internal_Use_Only\Entire_Geodatabase\Internal_USGS_Use_Only_National_Inventory_of_Dams_on_Medium_Resolution_NHDPlus_V2_for_CONUS.gdb\shortlist')
                           
            args = parser.parse_args()
            if not arcpy.Exists(args.dataset): raise Exception("Regions dataset does not exist")
            else : nidFC = args.dataset
            startTime = time.time()
            
            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'NIDconfig.json'))))  
            workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"]) 
            
            WiMLogging.init(os.path.join(workingDir,"Temp"),"Delineation.log")
            WiMLogging.sm("Started NID routine")

            #create new feature with fields ...
            desc = arcpy.Describe(nidFC)
            sr = desc.spatialReference

            tbl = self._createNIDTable(workingDir)          
            rows = arcpy.InsertCursor(tbl)

            with arcpy.da.SearchCursor(nidFC,["Shape@","Source_FeatureID"]) as source_curs:
                #fields = ['Source_FeatureID', 'Comments', 'COMID', 'COMDA_sqM','DA_sqM']
                for cur in source_curs: 
                    nidPoint = cur[0]
                    sfID = cur[1]
                    with HydroOps(workingDir,sfID) as hOps:                        
                        row = rows.newRow()
                        try:                            
                            row.setValue('Source_FeatureID',sfID)
                            nldibasin = self._getNLDIBasin(nidPoint[0], nidPoint.spatialReference)                            
                            
                            if(nldibasin == None or nldibasin["comid"]== None):
                                row.setValue('Comments',"NLDI Service failed to return catchments")
                                continue
                            row.setValue('COMID',str(nldibasin["comid"]))                        
                            globalArea = hOps.getAreaSqMeter(nldibasin["global"])
                            row.setValue('COMDA_Acre',globalArea*0.000247105)# in acres

                            hOps.Delineate(nidPoint, nldibasin["mask"])
                            hOps.MergeCatchment(nldibasin["global"])
                            Area = hOps.getAreaSqMeter(os.path.join(os.path.join(workingDir, hOps.WorkspaceID +'.gdb', "Layers"), Config()["catchment"]["global"]))
                            row.setValue('DA_Acre',Area*0.000247105)# in acres
                        except:
                            tb = traceback.format_exc()
                            row.setValue('Comments',"something went wrong ..." + tb[-200:])
                        finally:
                            rows.insertRow(row)
                            del row                   
                    #end hOps  
                    del nldibasin  
                #next cur
            #end source_curs        
             
            
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

    def _createNIDTable(self, directory):
        try:
            t_fields = (  
                         ("Source_FeatureID", "TEXT"),
                          ("DA_Acre", "DOUBLE"),                           
                         ("COMID", "TEXT"),
                         ("COMDA_Acre", "DOUBLE"),
                         ("Comments", "TEXT")                        
                         ) 

            datasetPath = arcpy.CreateFileGDB_management(directory, 'test.gdb')[0]
            table = arcpy.CreateTable_management(datasetPath, "NID_Area")

            for t_field in t_fields:  
                arcpy.AddField_management(table, *t_field)  

            return table[0]

        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error executing delineation wrapper "+tb)


    def _getNLDIBasin(self, point, sr):
        sa = None
        result={
            "comid":None,
            "mask":None,
            "global":None
            }
        try:
            sa = NLDIServiceAgent()

            maskjson = sa.getBasin(None,True,point.X,point.Y,sr.factoryCode)
            comid = maskjson[u'features'][0][u'properties'][u'featureid']
            result["comid"] = comid

            if(maskjson):
                mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC", "POLYGON", spatial_reference=sr) 
                if (maskjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(maskjson,mask,sr)
                else:
                    GeoJsonHandler.read_feature_collection(maskjson,mask,sr) 
                result["mask"] = mask
            
                basinjson = sa.getBasin(comid,False)

            if(basinjson):
                basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin", "POLYGON", spatial_reference=sr) 
                if (basinjson["type"].lower() =="feature"):
                    GeoJsonHandler.read_feature(basinjson,basin,sr)
                else:
                    GeoJsonHandler.read_feature_collection(basinjson,basin,sr)   
                result["global"] = basin

            return result

        except:
            tb = traceback.format_exc()
            WiMLogging.sm("Error executing delineation wrapper "+tb)
        finally:
            sa = None
class ReComputeAreaWrapper(object):
    #region Constructor
    def __init__(self):
        niddataset = None
        try:
            parser = argparse.ArgumentParser()
            #Use the following LAT/LON pour point
            parser.add_argument("-dataset", help="datasetpath", type=str, 
                                default = 'D:\WiM\Projects\NationalStreamStats\data\NID_Area\NID_Area.dbf')
                           
            args = parser.parse_args()
            if not arcpy.Exists(args.dataset): raise Exception("Regions dataset does not exist")
            else : niddataset = args.dataset
            startTime = time.time()
            
            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'NIDconfig.json'))))  
            workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"]) 
            
            WiMLogging.init(os.path.join(workingDir,"Temp"),"NIDrecomputeArea.log")
            WiMLogging.sm("Started NID routine")

            gdbPathlookup = self._getKeyDirectoryLookup(config["workingdirectory"])
            WiMLogging.sm("keyDirectory"+json.dumps(gdbPathlookup) )

            with arcpy.da.UpdateCursor(niddataset,["Source_Fea", "DA_Acre",'Comments']) as update_curs:
                for row in update_curs:                     
                    sfID = row[0]
                    try:
                        if not sfID in gdbPathlookup: 
                            WiMLogging.sm("Could not find sfid "+ sfID)
                            continue
                        basinGDB = gdbPathlookup[sfID]
  
                        with HydroOps(workingDir,sfID) as hOps: 
                            Area = hOps.getAreaSqMeter(basinGDB) #GA06020
                            if Area == None: raise Exception("Area is none")
                            row[2]="oldvalue"+str(row[1])+row[2]
                            row[1]=Area*0.000247105 # in acres
                            update_curs.updateRow(row)
                    
                    except:
                        tb = traceback.format_exc()
                        row[2] = "something went wrong ..." + tb[-200:]
                        update_curs.updateRow(row)
                #next cur
            #end update_curs        
             
            
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

    def _getFileGDB(self, dir, file):
        gdbsList = []
        for dirpath,dirnames,filenames in os.walk(dir):
            if (file in dirnames): 
                gdbsList.append(os.path.join(dirpath, file))
            #remove gdb folders in order to exclude walk
            [dirnames.remove(d) for d in list(dirnames) if d.endswith(".gdb")]
        #next
        return gdbsList 
    def _getKeyDirectoryLookup(self, dir):
        keyList = {}
        for dirpath,dirnames,filenames in os.walk(dir):
            for d in list(dirnames):
                if d.endswith(".gdb"):
                    key = d.replace(".gdb","")
                    if key in keyList: 
                        #check if original has global
                        if arcpy.Exists(os.path.join(os.path.join(keyList[key], "Layers"), Config()["catchment"]["global"])):
                            WiMLogging.sm("DuplicatedWorkspace sticking with original,"+keyList[key]+" Other, "+ os.path.join(dirpath, d))
                        else:
                            WiMLogging.sm("No global removing gdb,"+keyList[key])
                            shutil.rmtree(keyList[key], ignore_errors=True)
                            keyList[key] = os.path.join(dirpath, d,"Layers",Config()["catchment"]["global"])
                    else: 
                        keyList[key] = os.path.join(dirpath, d,"Layers",Config()["catchment"]["global"])


            #remove gdb folders in order to exclude walk
            [dirnames.remove(d) for d in list(dirnames) if d.endswith(".gdb")]
        #next
        return keyList   

if __name__ == '__main__':
    #DelineationWrapper()
    ReComputeAreaWrapper()

