'''
Created on Mar 16, 2017

@author: gpetrochenkov
'''

import numpy as np
import netCDF4
from datetime import datetime

#dictionary functions to compute statistic
stats_funcs = {
    'MEAN': lambda data: np.mean(data),
    'MINIMUM': lambda data: np.min(data),
    'MAXIMUM': lambda data: np.max(data),
    'STD': lambda data: np.std(data),
    'UNIQUEVALUECOUNT': lambda data: len(np.unique(data))
}

#timeRange is set to 2-1-2014 by default
def get_statistic(rasterCellIdx, dataPath, statisticRule,
                  timeRange = (datetime(2014,2,1),datetime(2014,2,1))):
    
    #open netCDF file
    with netCDF4.Dataset(dataPath, 'r') as ds:
        
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
        
        row, column = np.where(rasterCellIdx != -9999.00)
        rasterCellIdx = np.unique(rasterCellIdx[row,column]).astype(np.int) 
        
        #get the data via the time index and raster cell indexes
        data = ds.variables['data'][startTimeIdx:endTimeIdx,rasterCellIdx] / 100.
        
        return stats_funcs[statisticRule](data)
        
        
    
    

    