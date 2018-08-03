#------------------------------------------------------------------------------
#----- Main_Multiprocess.py -----------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2018 WiM - USGS
#
#    authors:  Greg Petrochenkov 
#              
#    purpose:  the buck start here w/ multiprocess support
#
#      dates:   21 Feb 2018 gp - created
#               03 Aug 2018 jkn - update 
#
#------------------------------------------------------------------------------

#region "Imports"
import sys
import numpy as np
import gc
import arcpy #Left in so that arcpy does not have to be loaded more than once for child processes
import multiprocessing as mp
import os

import argparse
import json
import traceback
import string

from FederalHighwayWrapper import FederalHyghwayWrapper
from Resources import gage

from WIMLib import Shared
from WIMLib import WiMLogging
from WIMLib.Config import Config
#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main mulitprocess
##-------+---------+---------+---------+---------+---------+---------+---------+

class Main_Multiprocess(object):
    #region Constructor
    def __init__(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-projectID", help="specifies the projectID", type=str, default="FH")
            parser.add_argument("-file", help="specifies csv file location including gage lat/long and comid's to estimate", type=str, 
                                default = 'D:\\WiM\\Projects\\NationalStreamStats\\gagesiii_lat_lon.csv')
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "TOT_NID_DISTURBANCE_INDEX")  

                           
            args = parser.parse_args()            
            projectID = args.projectID
            if projectID == '#' or not projectID:
                raise Exception('Input Study Area required')

            config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json')))) 
            workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"],projectID)           
                 
            WiMLogging.init(os.path.join(workingDir,"Temp"),"gage.log")
            WiMLogging.sm("Starting routine")
            
            params =  args.parameters.split(";") if(args.parameters)else config["characteristics"].keys()

            file = Shared.readCSVFile(args.file)
            headers = file[0]
            if "gage_no_1" in headers: idindex = headers.index("gage_no_1")
            if "gage_name" in headers: nmindex = headers.index("gage_name")
            if "COMID" in headers: comIDindex = headers.index("COMID")
            if "lat" in headers: latindex = headers.index("lat")
            if "lon" in headers: longindex = headers.index("lon")
            #strip the header line
            file.pop(0)
            header =[]
            header.append("-+-+-+-+-+-+-+-+-+ NEW RUN -+-+-+-+-+-+-+-+-+")
            header.append("Execute Date: " + str(datetime.date.today()))
            header.append("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")   
                
            header.append(",".join(['COMID','WorkspaceID','Description','LAT','LONG']+self._formatRow(params)))

            Shared.writeToFile(os.path.join(workingDir,config["outputFile"]),header)


            #Number of processes to split the full count of gages in to
            split = 10
            gageChunks = np.array_split(np.array(file),split)

            #Although not used for two way pipes, always good to collect processes/pipes in case of future revisions
            processes = []
            pipes = []
    
            #Array used for concurrency locks
            arr = mp.Array('c', 1000)
            for chunk in gageChunks:                
                send, recieve = mp.Pipe()
                #add pipe to array
                pipes.append((send,recieve))                  
                #Create process and assign target and arguments
                p = mp.Process(target = self._run, args=[send, arr])
                #Send arguments to the pipe
                recieve.send([projectID,workingDir,chunk,params])       
                #Add process to list
                processes.append(p)                
                p.start()
            #next x         
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("error running "+tb)
    
    def _run(self,projectID, workingDir, gagelist, outwkid, params):
        try:


            with FederalHyghwayWrapper(workingDir, projectID) as fh:                
                for station in gagelist:
                    results={'Values':[{}]}
                    try:
                        g = gage.gage(station[idindex],station[comIDindex],station[latindex],station[longindex],args.outwkid,station[nmindex])
                        results = fh.Run(g, params)  
                    
                        if results is None: results={'Values':[{}]}
                        Shared.appendLineToFile(os.path.join(workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,fh.workspaceID,results.Description,g.lat,g.long]+self._formatRow(results.Values,True)))
                    except:
                        tb = traceback.format_exc()
                        WiMLogging.sm("error computing gage "+g.id+" "+tb)
                        continue
                    finally:
                        #ensure gc has collected before next gage
                        gc.collect()
                #next station
            #endwith

            pass
        except:
            pass
    def _formatRow(self, params, hasKeys =False):        
            r = []
            keys = params if not hasKeys else params.keys()
            for k in keys:
                for p_val in ['localvalue','totalvalue','globalvalue']:
                    value = str(k) + "_" + str(p_val) if not hasKeys else params[k][p_val]
                    r.append(value)
                #next p_val
            #next p

            return r
    

if __name__ == '__main__':
    Main_Multiprocess()