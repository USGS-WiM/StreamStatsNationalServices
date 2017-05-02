'''
Created on Apr 10, 2017

@author: gpetrochenkov
'''

from Resources.gage import gage
import json
import os
import numpy as np
import arcpy
from WiMLib import WiMLogging
from Resources.Characteristic import Characteristic
from WiMLib.Resources import Result
from WiMLib import Shared
from WiMLib import GeoJsonHandler
from WiMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
from Ops.StreamStatsNationalOps import *
from Ops.HydroOps import HydroOps
from time import time
from RestAPI.utilities import *
      
def delineate(**kargs):
    '''intermediate for the delineation work'''
    
    #get data
    arg_data = kargs['data']
    xpoint = float(arg_data['xlocation'])
    ypoint = float(arg_data['ylocation'])
    crs = int(arg_data['crs'])
    
    comID = None
    if 'comID' in arg_data:
        comID = int(arg_data['comID'])
    
    #set up config information
    config = get_config()
    workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],'FH')   
    WiMLogging.init(os.path.join(workingDir,"Temp"),"gage3.log")
    
    #get appropriate guage via either x/y point or comID
    gauge = get_gauge(xpoint, ypoint, crs, comID)
    
    #perform delineation task and get back the workspace,
    #basin featureClass, and pourpoint featureClass
    workspaceID, basin, ppoint = _delineate(gauge,workingDir)
    
    #convert data in to geojson
    featureCollection = get_delineation_features(ppoint, basin, crs)
    
    #arrange return data
    data = {}
    data['workspaceID'] = workspaceID
    data['featureCollection'] = featureCollection
    data['messages'] = [{'message': 'success'}]
    
    #if include Parameters is not in args or not False
    #compute each charactersitic or all if True
    if 'includeParameters' not in arg_data:
        arg_data['includeParameters'] = True
        
    #return data
    if arg_data['includeParameters'] != False:
        arg_data['workspaceID'] = workspaceID
        data['parameters'] = basin_chars(data=arg_data)
    
    return data
    
def _delineate(gage, workspace):
        '''Main worker for the delineation of catchments'''
    
        #create pour point in memory and read in features
        ppoint = arcpy.CreateFeatureclass_management("in_memory", "ppFC"+gage.comid, "POINT", spatial_reference=gage.sr)
        pnt = {"type":"Feature","geometry":{"type":"Point","coordinates":[gage.lat,gage.long]}} 
        if (pnt["type"].lower() =="feature"):
            GeoJsonHandler.read_feature(pnt,ppoint,gage.sr)
        else:
            GeoJsonHandler.read_feature_collection(pnt,ppoint,gage.sr)  

        #get basin for  gauge
        sa = NLDIServiceAgent()
        maskjson = sa.getBasin(gage.comid,True)

        if(not maskjson): return None

        #create in memory basin featureClass and read in properties
        mask = arcpy.CreateFeatureclass_management("in_memory", "maskFC"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
        if (maskjson["type"].lower() =="feature"):
            GeoJsonHandler.read_feature(maskjson,mask,gage.sr)
        else:
            GeoJsonHandler.read_feature_collection(maskjson,mask,gage.sr) 
        
        basinjson = sa.getBasin(gage.comid,False)

        if(not basinjson): return None

        #create in memory basin featureClass and read in properties
        basin = arcpy.CreateFeatureclass_management("in_memory", "globalBasin"+gage.comid, "POLYGON", spatial_reference=gage.sr) 
        if (basinjson["type"].lower() =="feature"):
            GeoJsonHandler.read_feature(basinjson,basin,gage.sr)
        else:
            GeoJsonHandler.read_feature_collection(basinjson,basin,gage.sr)         
                
        #go throught delineation process and merge the associated catchments
        ssdel = HydroOps(workspace,gage.comid)
        ssdel.Delineate(ppoint, mask)
        ssdel.MergeCatchment(basin)
        
        #find slice of workspace to return to the user
        slice_idx = workspace.rfind('\\') + 1
        slice_idx2 = workspace.rfind('/') + 1
        slice_idx = np.max([slice_idx,slice_idx2])
        
        return [workspace[slice_idx:], basin, ppoint]
    
    
def basin_chars(**kwargs):
    '''intermediate for compusting charactersitics worker'''
    
    data_dict = kwargs['data']
    
    config = get_config()
    
    #list all available charactersitics if no workspace is provided
    if 'workspaceID' not in data_dict or data_dict['worspaceID'] == '':
       
        characteristics = []
      
        for x in config["characteristics"]:
            characteristics.append(get_characteristic_dict(Characteristic(x)))
                
        return characteristics
    
    else:
        
        #create full path for the workspace
        workspace = os.path.join(config["workingdirectory"], data_dict['workspaceID'])
        
        #crawl the directory of workspace to get the comID
        comId = get_com_id(workspace)
               
        #get the appropriate spatial reference  
        sr = get_spatial_reference(workspace, comId)
                
        #get the appropriate gauge
        gauge = get_gauge(None, None, None, int(comId), sr)
                    
               
        #if includeParameters not in args then return all characteristics    
        #otherwise compute only those that are listed 
        if 'includeParameters' not in data_dict:
            data_dict['includeParameters'] = True
            
        
        if data_dict['includeParameters'] == True or data_dict['includeParameters'] == False:
            characteristics =_computeCharacteristics(gauge, workspace, comId, config["characteristics"])
                 
        else:
            characteristics =_computeCharacteristics(gauge, workspace, comId, data_dict['includeParameters'])
        
        return characteristics
        
        
def _computeCharacteristics(gage,workspace,workspaceID,parameters):
    '''main worker for compute basin charactersitics'''
    
    method = None

    WiMResults = Result.Result(gage.comid,"Characteristics computed for "+gage.name)
    
    #get the global basin values from NLDI (just a csv for now)
    with NLDIServiceAgent() as sa:

        globalValue = sa.getBasinCharacteristics(gage.comid)
        
    #end with
    startTime = time()
    
    #open up stream stats ops and compute the characteristics
    characteristics = []
    with StreamStatsNationalOps(workspace, workspaceID) as sOps: 
                    
        #for all chars in the parameters
        for p in parameters:
            method = None
            
            parameter = Characteristic(p)
            if(not parameter): 
               
                continue

            method = getattr(sOps, parameter.Procedure) 
            
            #if method exists get value
            if (method): 
                result = method(parameter) 
                #todo:merge with request from NLDI
                
                #get the value minus the global value and add the characteristic
                #to the final list
                if(parameter.Name in globalValue):
                    
                    char_value = float(globalValue[parameter.Name])-result[parameter.Name]
                    characteristics.append(
                        get_characteristic_dict(parameter, char_value)
                        )

                WiMResults.Values.update(result)
            else:
                
                continue 
                  
    print 'Finished.  Total time elapsed:', str(round((time()- startTime)/60, 2)), 'minutes'

    #return the characteristics
    return characteristics

    
    
        