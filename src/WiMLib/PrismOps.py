#------------------------------------------------------------------------------
#----- PrismOps.py ------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Greg Petrochenkov - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Handles PRISIM data for the StreamStats project
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:  16 MAR 2017 gp - Created / Date notation edited by jw
#              04 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

import numpy as np
import netCDF4
from datetime import datetime

#dictionary functions to compute statistic
stats_funcs = {
    'SUM': lambda data: np.sum(data, 1),
    'MEAN': lambda data: np.mean(data),
    'MINIMUM': lambda data: np.min(data),
    'MAXIMUM': lambda data: np.max(data),
    'STD': lambda data: np.std(data),
    'UNIQUEVALUECOUNT': lambda data: len(np.unique(data))
}

#timeRange is set to 2-1-2014 by default
def get_statistic(rasterCellIdx, dataPath, statisticRules,
                  timeRange = (datetime(2014,2,1),datetime(2014,2,1)), timeMethod="SUM/MEAN"):
    
    #open netCDF file
    with netCDF4.Dataset(dataPath, 'r') as ds:
        
        time = ds.variables['time']
        
        #convert time in to array of datetimes
        dates = netCDF4.num2date(time[:], time.units, calendar='standard')
        
        #get the start and end indices for the time dimension
        #based on the time method
        arrangedDts = arrangeTimeIdx(dates, timeRange, timeMethod)
        
        #Get the raster indices of the 
        row, column = np.where(rasterCellIdx != -9999.00)
        rasterCellIdx = np.unique(rasterCellIdx[row,column].astype(np.int))
        
        #get the data via the time index and raster cell indexes
        data = [ds.variables['data'][x[0]:x[1],rasterCellIdx] / 10000. for x in arrangedDts]
        
        #Run statistics on data
        for x in statisticRules:
            data = stats_funcs[x](data)
            
        return data
    
def arrangeTimeIdx(dates, time_range, method):
    
    if method == 'MeanMonth':
        
        final_idx = []
        current, end = time_range[0], time_range[1]
        
        while current < end:
            if current.month == 12:
                month = 1
                year = current.year + 1
            else:
                month = current.month + 1
                
            next_date = datetime(year, month, current.day)
            start_time_idx = np.abs(np.array(current - dates)).argmin()
            end_time_idx = np.abs(np.array(next_date - dates)).argmin()
            
            final_idx.append([start_time_idx, end_time_idx])
            
            current = next_date
            
    elif method == 'MeanYear':
            
        final_idx = []
        current, end = time_range[0], time_range[1]
        
        while current < end:
            
            year = current.year + 1
            
            next_date = datetime(year, current.month, current.day)
            start_time_idx = np.abs(np.array(current - dates)).argmin()
            end_time_idx = np.abs(np.array(next_date - dates)).argmin()
            
            final_idx.append([start_time_idx, end_time_idx])
            
            current = next_date
            
    elif method == 'MonthSpecific':
        
        final_idx = []
        current, end = time_range[0], time_range[1]
        
        while current <= end:
            if current.month == 12:
                month = 1
                year = current.year + 1
            else:
                month = current.month + 1
                
            next_date = datetime(year, month, current.day)
            start_time_idx = np.abs(np.array(current - dates)).argmin()
            end_time_idx = np.abs(np.array(next_date - dates)).argmin()
            
            final_idx.append([start_time_idx, end_time_idx])
            
            current = datetime(current.year + 1, current.month, current.day)
            
    return final_idx
        
        
    
    

    