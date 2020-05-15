'''
Created on Apr 21, 2017

@author: gpetrochenkov
'''

from Resources.gage import gage
import json
import os
from arcpy import SpatialReference
import numpy as np
import arcpy
from WIMLib import WiMLogging
from Resources.Characteristic import Characteristic
from WIMLib.Resources import Result
from WIMLib import Shared
from WIMLib import GeoJsonHandler
from WIMLib.Config import Config
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
from Ops.StreamStatsNationalOps import *
from Ops.HydroOps import HydroOps
from geojson import Point, Polygon, Feature, FeatureCollection


from geojson.feature import FeatureCollection
def get_comma_sep_values(paramString):
    '''Method to return either a plit array of arguments or True or False'''
    
    if paramString.lower() == 'true':
        return True
    elif paramString.lower() == 'false':
        return False
    else:
        return paramString.split(',')
    
def validate_format(input_format, formats):
    if input_format not in formats:
        raise Exception('Output format %s not available for query type' \
                        % input_format)
    else:
        return input_format
    
def check_exists(parameter, arguments):
    if parameter not in arguments:
        raise Exception('Missing parameter: %s' % parameter)
    else:
        return arguments[parameter]

def get_config():
    return Config(json.load(open(os.path.join(os.path.dirname(__file__),'../config.json')))) 

def get_gauge(xpoint, ypoint, crs, comid=None, in_sr = None):
    '''gets the gauge according to x/y points or comid'''
    
    #get the spatial reference
    if in_sr is None:
        sr = SpatialReference(crs)  
    else:
        sr = in_sr
    
    #read in the csv file with all of the gauges
    gauge_file = Shared.readCSVFile('C:\\GIS\\gagesiii_lat_lon.csv')
    headers = gauge_file[0]
    if "gage_no_1" in headers: idindex = headers.index("gage_no_1")
    if "gage_name" in headers: nmindex = headers.index("gage_name")
    if "COMID" in headers: comIDindex = headers.index("COMID")
    if "lat" in headers: latindex = headers.index("lat")
    if "lon" in headers: longindex = headers.index("lon")

    #remove header
    gauge_file.pop(0)
  
    #create all gauges and get the gauge closest to the provided x and y points
    gauge_data = []
    for station in gauge_file:
        gauge_data.append(gage(station[idindex],station[comIDindex],station[latindex],station[longindex],sr,station[nmindex]))
        
    if comid is None:
        gauge_idx = np.array([np.abs((float(x.lat) - xpoint)) + np.abs((float(x.long) - ypoint)) for x in gauge_data]).argmin()
    else:
        gauge_idx = np.array([np.abs(int(x.comid) - comid) for x in gauge_data]).argmin()
    
    return gauge_data[gauge_idx]

def get_com_id(workspace):
    
    for root, dirs, files in os.walk(workspace):
        for name in dirs:
            if name.find('gdb') != -1:
                return name[:-4]
            
def get_spatial_reference(workspace, comId):
    
    arcpy.env.workspace = '%s/%s.gdb' % (workspace, comId) 
    datasets = arcpy.ListDatasets()
    
    for dataset in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
                sr = arcpy.Describe(fc).spatialReference
                break
def get_characteristic_dict(characteristic, value=None):
    
    char_dict =  {
                'name': characteristic.Name,
                'description': characteristic.Description,
                'code': characteristic.Procedure,
                'unit': characteristic.UnitID 
                }
    
    if value is not None:
        char_dict['value'] = value
        
    return char_dict

def get_delineation_features(ppoint, basin, crs):
    
    CRS = {'type' : 'ESPG', 'properties': {'code': crs}}
    
    # Enter for loop for each feature
    for row in arcpy.da.SearchCursor(ppoint, ["SHAPE@XY"]):
        x, y = row[0]
        globalwatershedpoint = Feature(id="globalwatershedpoint", 
                                       geometry=Point((x,y)))
        globalwatershedpoint['crs'] = CRS
        
    for row in arcpy.da.SearchCursor(basin, ["SHAPE@"]):
        
        for part in row[0]:

            points = []
            
            for pnt in part:
                points.append((pnt.X, pnt.Y))
                
            globalwatershed = Feature(id="globalwatershed", 
                                       geometry=Polygon(points))
            globalwatershed['crs'] = CRS
            
    return FeatureCollection([globalwatershedpoint, globalwatershed])