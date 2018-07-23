'''
Created on Feb 21, 2018

@author: gpetrochenkov
'''

from FederalHighwayWrapper2 import delineationWrapper
import sys
import numpy as np
import gc
import arcpy #Left in so that arcpy does not have to be loaded more than once for child processes
import multiprocessing as mp
import os


#Method to run a new process with the appropriate list of gages
def runFH(conn, arr):

    #Send via pipe name of the directory, the start, and end indices of gage list
    name, start_idx, end_idx = conn.recv()

    rang = range(start_idx,end_idx+1)
    start = rang[:-1]
    end = rang[1:]
    
    #For each number in the gage indices
    for x,y in zip(start,end):
        
        #Give an approx second for each process to begin so that they cascade attributes during processing
        import time
        time.sleep(1.1)
        
        #Create temp directory so ARC does not run out of internal memory
        newTempDir = r"D:\Applications\output\gage_iii\temp\gptmpenvr_" + time.strftime('%Y%m%d%H%M%S') + '2018' + str(x)
        os.mkdir(newTempDir)
        os.environ["TEMP"] = newTempDir
        os.environ["TMP"] = newTempDir
        
        
        #Run process until it finished successfully
        #Errors aside from fatal crashes are not accounted for here
        full_run = False
        
        while full_run == False:
            try:
                #Run delineation wrapper on this gage
                #Collect garbage afterwards
                delineationWrapper(x, y, name, arr)
                full_run = True
                gc.collect()
                
            except:
                continue


if __name__ == '__main__':

    #Number of processes to split the full count of gages in to
    split = 10
    gage_len = np.arange(14307)
    gage_len_split = np.array_split(gage_len, split)
    
    #Although not used for two way pipes, always good to collect processes/pipes in case of future revisions
    processes = []
    pipes = []
    
    #Array used for concurrency locks
    arr = mp.Array('c', 1000)
    
    for x in range(split):
        gage_section = gage_len_split[x][::1]
        
        send, recieve = mp.Pipe()
        pipes.append((send,recieve))
        
        #Create process and assign target and arguments
        p = mp.Process(target = runFH, args=[send, arr])
       
        #Send arguments to the pipe
        recieve.send(['//FH%d' % x, gage_section[0], gage_section[-1]])
       
        #Add process to list
        processes.append(p)
#        
        p.start()
#         
    
