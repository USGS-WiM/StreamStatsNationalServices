'''
Created on Mar 16, 2017

@author: gpetrochenkov
'''

import numpy as np
import netCDF4
from datetime import datetime

# to be completed with a function to map with the statistics
# with its respective netCDF file
def map_data(statistic):
    return "C:\\Projects\\General\\pptint.nc"

#dictionary functions to compute statistic
stats_funcs = {
    'MEAN': lambda data: np.mean(data),
    'MINIMUM': lambda data: np.min(data),
    'MAXIMUM': lambda data: np.max(data),
    'STD': lambda data: np.std(data),
    'UNIQUEVALUECOUNT': lambda data: len(np.unique(data))
}

#timeRange is set to 2-1-2014 by default
def get_statistic(rasterCellIdx, statistic, statisticRule,
                  timeRange = (datetime(2014,2,1),datetime(2014,2,1))):
    
    #get the netCDF file path from mao_data function
    netCDF_file = map_data(statistic)
    
    #open netCDF file
    with netCDF4.Dataset(netCDF_file, 'r') as ds:
        
        time = ds.variables['time']
        
        #convert time in to array of datetimes
        dates = netCDF4.num2date(time[:], time.units, calendar='standard')
        
        #get the start and end index for time dimension
        startTimeIdx = np.array(timeRange[0] - dates).argmin()
        endTimeIdx = np.array(timeRange[1] - dates).argmin()
        
        #if they are the same increment the endTimeIdx so that at one data
        #set is pulled
        if startTimeIdx == endTimeIdx:
            endTimeIdx += 1
        
        #get the data via the time index and raster cell indexes
        data = ds.variables['data'][startTimeIdx:endTimeIdx,rasterCellIdx]
        
        return stats_funcs[statisticRule](data)
        
        
    
    

    