'''
Created on Feb 21, 2018

@author: gpetrochenkov
'''

import pandas as pd
import numpy as np
import os
import shutil
import datetime
import arcpy
import traceback

class Stitch(object):
    def __init__(self, date):
        self.__resultfolder__ = ""
        self.__date__ = date
        self.__run__()
    def __enter__(self):
        return self
    def __run__(self):
        df_list = []
        first = True
        columns = None

        ignore_files = ['.csv']
        fill_blanks = False
        get_gdbs = True
        skip = []
        processes = 10

        #If files already exist delete them
        if os.path.exists('D:\Applications\output\gage_iii\splitCatchmentFinal.csv'):
            os.remove('D:\Applications\output\gage_iii\splitCatchmentFinal.csv')

        for x in range(processes):

            #So you will have to rename the new folders e.g.: from FH-098120398123 to FH0
            # once the run is done the this is written now.  Not too cumbersome seeing as we're only running
            #10 processes but may want to walk through the directory as recently modified
            #if we start using more cause it could get annoying after a while
            file_name = r'D:\Applications\output\gage_iii\temp\FH-%d_%s\splitCatchment.csv' % (x, self.__date__)

            #Append all data from splitCatchment.csv files, account for first file's headers
            if first == True:
                df_list.append(pd.read_csv(file_name, sep=',', skiprows=3,
                                           dtype={'GAGEID': str,
                                                  'TOT_BASIN_AREA_totalvalue': str,
                                                  'TOT_BASIN_AREA_globalvalue': str,
                                                  'TOT_BASIN_AREA_localvalue': str}))
                columns = df_list[0].columns
                first = False
            else:
                try:
                    temp_df = pd.read_csv(file_name, sep=',', skiprows=4, header=None,
                                               dtype={'GAGEID': str,
                                                      'TOT_BASIN_AREA_totalvalue': str,
                                                      'TOT_BASIN_AREA_globalvalue': str,
                                                      'TOT_BASIN_AREA_localvalue': str})
                    a = temp_df.columns
                    temp_df.columns = columns
                    df_list.append(temp_df)
                except:
                    print'nodata'
                    skip.append(x)

        #Concatenate all data frames in to one and sort columns alphabetically
        master_df = pd.concat(df_list)
        master_df = master_df.reindex_axis(np.concatenate([master_df.columns[:7],sorted(master_df.columns[7:])]), axis=1)

        #If setting is true, change values that are blank to 0
        if fill_blanks:
            cols = master_df.columns[7:]
            for x in cols:
                master_df[x][np.isnan(master_df[x].values)] = 0

        #Save combined and sorted data frame
        master_df.to_csv(path_or_buf=r'D:\Applications\output\gage_iii\splitCatchmentFinal.csv')

        ignore_files = ['.csv']
        self.__checkfolder__('D:\Applications\output\gage_iii\ResultSet' + self.__date__, 0)
        dest_base = os.path.join(self.__resultfolder__, 'gdb')
        if not arcpy.Exists(dest_base):
            os.makedirs(dest_base)


        if get_gdbs == True:
            #Remove all old GDBs still in folder
            for root, sub_folders, files in os.walk(dest_base):
                for s in sub_folders:
                    shutil.rmtree( ''.join([dest_base, '\\', s]))

            #Copy all GDBs in to folder
            for x in range(processes):
                if x not in skip:
                    path_base = r"D:\Applications\output\gage_iii\temp\FH-%d_%s" % (x, self.__date__)

                    for root, sub_folders, files in os.walk(path_base):
                        for s in sub_folders:
                            try:
                                format_path = s.replace(path_base, '')
                                if format_path[-3:] == 'gdb' and not os.path.exists(''.join([dest_base, '\\', s])):
                                    shutil.copytree(''.join([root, '\\', s]),
                                                        ''.join([dest_base, '\\', s]))
                            except:
                                tb = traceback.format_exc()
                                print tb
        shutil.copy2('D:\Applications\output\gage_iii\splitCatchmentFinal.csv', self.__resultfolder__)

    def __checkfolder__(self, folder, i):
        if i == 0:
            checkFolder = folder
            i += 1
        else:
            checkFolder = folder + " " + str(i)
            i += 1
        if arcpy.Exists(checkFolder):
            self.__checkfolder__(folder, i)
        else:
            self.__resultfolder__ = checkFolder
        
    
        

