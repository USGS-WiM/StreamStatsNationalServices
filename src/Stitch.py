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
        if os.path.exists('D:\stitch\splitCatchmentFinal.csv'):
            os.remove('D:\stitch\splitCatchmentFinal.csv')

        for x in range(processes):

            #So you will have to rename the new folders e.g.: from FH-098120398123 to FH0
            # once the run is done the this is written now.  Not too cumbersome seeing as we're only running
            #10 processes but may want to walk through the directory as recently modified
            #if we start using more cause it could get annoying after a while
            file_name = 'D:\Applications\output\gage_iii\FH-%d %s\splitCatchment.csv' % (x, self.__date__)

            #Append all data from splitCatchment.csv files, account for first file's headers
            if first == True:
                df_list.append(pd.read_csv(file_name, sep=',', skiprows=3))
                columns = df_list[0].columns
                first = False
            else:
                try:
                    temp_df = pd.read_csv(file_name, sep=',', skiprows=4, header=None)
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
        master_df.to_csv(path_or_buf='D:\\stitch\\splitCatchmentFinal.csv')

        ignore_files = ['.csv']
        dest_base = "D:\stitch\gdb"


        if get_gdbs == True:
            #Remove all old GDBs still in folder
            for root, sub_folders, files in os.walk(dest_base):
                for s in sub_folders:
                    shutil.rmtree( ''.join([dest_base, '\\', s]))

            #Copy all GDBs in to folder
            for x in range(processes):
                if x not in skip:
                    path_base = "D:\Applications\output\gage_iii\FH-%d %s" % (x, self.__date__)

                    for root, sub_folders, files in os.walk(path_base):
                        for s in sub_folders:
                            format_path = s.replace(path_base, '')
                            if format_path[-3:] == 'gdb' and not os.path.exists(''.join([dest_base, '\\', s])):
                                shutil.copytree(''.join([root, '\\', s]),
                                                    ''.join([dest_base, '\\', s]))
        #date = datetime.datetime.today().strftime('%#m-%d-%Y')
        self.__checkfolder__('D:\stitch\Result Set ' + self.__date__, 0)
        shutil.copytree(dest_base, self.__resultfolder__)
        shutil.copy2('D:\stitch\splitCatchmentFinal.csv', self.__resultfolder__)

    def __checkfolder__(self, folder, i):
        i += 1
        if arcpy.Exists(folder + " " + str(i)):
            self.__checkfolder__(folder, i)
        else:
            self.__resultfolder__ = folder + " " + str(i)
        
    
        

