'''
Created on Feb 21, 2018

@author: gpetrochenkov
'''

from FederalHighwayWrapper2 import delineationWrapper
import sys
import numpy as np
import gc
import arcpy
import multiprocessing as mp
import os

 
def runFH(conn, arr):

    name, start_idx, end_idx = conn.recv()

    rang = range(start_idx,end_idx+1)
    start = rang[:-1]
    end = rang[1:]
    
    for x,y in zip(start,end):
#         conn.send((x,end[-1]))
        full_run = False
        import time
        time.sleep(1.1)
        newTempDir = r"E:\Applications\output\gage_iii\temp\gptmpenvr_" + time.strftime('%Y%m%d%H%M%S') + '2018' + str(x)
        os.mkdir(newTempDir)
        os.environ["TEMP"] = newTempDir
        os.environ["TMP"] = newTempDir
        
        while full_run == False:
            try:
                delineationWrapper(x, y, name, arr)
                full_run = True
                gc.collect()
                
            except:
                continue

if __name__ == '__main__':
   
   
    split = 8
    gage_len = np.arange(756)
    gage_len_split = np.array_split(gage_len, split)
    processes = []
    pipes = []
    arr = mp.Array('c', 1000)
    for x in range(split):
        gage_section = gage_len_split[x][::1]
        
        send, recieve = mp.Pipe()
        pipes.append((send,recieve))
        
        
        p = mp.Process(target = runFH, args=[send, arr])
       
        recieve.send(['//FH%d' % x, gage_section[0], gage_section[-1]])
       
        processes.append(p)
#        
        p.start()
#         
    
