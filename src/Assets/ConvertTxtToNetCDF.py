'''
Created on Mar 15, 2017

@author: gpetrochenkov
'''
import numpy as np
import netCDF4
from datetime import datetime


#input parameters
in_file_name = r'C:\Users\gpetrochenkov\Downloads\Wolock_prism-20171206T165217Z-001\Wolock_prism\pptint\pptint.txt'
output_file_name = r'C:\Users\gpetrochenkov\Downloads\Wolock_prism-20171206T165217Z-001\Wolock_prism\pptint\pptint.nc'
month = 1
year = 1945
#I am going to consult some coworkers regarding naming and attribute conventions
#for raster netCDF files, granted these are made merely for convenience and not for
#distribution
variable_name = 'data'
variable_desc = 'precipitation'
number_of_valid_cells = 481631

#inferred_parameter (beginning date time)
dt_static = datetime(year,month,1)

#open a new netCDF file or overwrite an old one
with netCDF4.Dataset(output_file_name, "w") as ds:
    
    #create netCDF dimensions
    time_dim = ds.createDimension("time", size=None)
    idx_dim = ds.createDimension("raster_cell_index", size=number_of_valid_cells)
    
    #create time variable (days since beginning date)
    time = ds.createVariable("time", 'f8', ('time'))
    time.setncattr("units", "days since %d-%d-1 UTC" % (year, month))
    
    #create cell index variable for all cells with data raster
    raster_cell_idx = ds.createVariable("raster_cell_index", 'i4', ('raster_cell_index'))
    raster_cell_idx.setncattr("description", "Raster index of associated prism data")
    raster_cell_idx[:] = np.arange(0,number_of_valid_cells)
    
    data_var = ds.createVariable(variable_name, 'f8', ('time', 'raster_cell_index'))
    data_var.setncattr("description", ''.join(['prism data for ',variable_desc]))
    
    #get initial amount of days from beginning
    time_delta = (datetime(year, month, 1) - dt_static).days
    val_count = 0
    
    #open text file
    with open(in_file_name, 'r') as txt_file:
        
        # number of cells to read for one month and indices
        val_count_max = number_of_valid_cells + 2
        month_values = []
        time_idx = 0
       
        #read lines til EOF
        for line in txt_file:
            
            #Get values, number of values and update val_count
            vals = str(line).replace('\n', '').split(' ')[1:]
            current_count = len(vals)
            val_count += current_count
            
            #if val count is gt_or_eq val_count_max
            if val_count >= val_count_max:
               
                #add the number of values up to the appropriate index
                for x in range(0,current_count - (val_count - val_count_max)):
                    month_values.append(vals[x])
                
                #get number of days in time delta to add to time variable
                time[time_idx] = time_delta
                
                #add the monthly values
                data_var[time_idx,:] = month_values[2:]
                
                #increment time index, month, and year accordingly
                time_idx += 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                   
                #get new amount of days from beginning for next month
                time_delta = (datetime(year, month, 1) - dt_static).days
                
                #initialize month values and add any remaining values in line
                month_values = []
                for x in range(current_count - (val_count - val_count_max), \
                                len(vals)):
                    month_values.append(vals[x])
                  
                #update value count  
                val_count -= val_count_max
                    
            else:
                    
                #add each value found in line
                for x in vals:
                    month_values.append(x)
                    
print('done converting')