#------------------------------------------------------------------------------
#----- Main.py -----------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  20168 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  the buck start here
#
#      dates:   02 AUG 2018 jkn 
#
#------------------------------------------------------------------------------

#region "Imports"
import argparse
import json
import traceback
import string
import os
import gc

from FederalHighwayWrapper import FederalHighwayWrapper
from Resources import gage

from WIMLib import Shared
from WIMLib import WiMLogging
from WIMLib.Config import Config
#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main
##-------+---------+---------+---------+---------+---------+---------+---------+

class Main(object):
    #region Constructor
    def __init__(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-projectID", help="specifies the projectID", type=str, default="FH_short")
            parser.add_argument("-file", help="specifies csv file location including gage lat/long and comid's to estimate", type=str, 
                                default = r'D:\Applications\input\CATCHMENT_gageloc_v1_short.csv')
            parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int, 
                                default = '4326')
            parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed", type=str, 
                                      default = "TOT_BASIN_AREA;" \
                                        +"TOT_IMPV11;" \
                                        +"TOT_IMPV11_NODATA;"\
                                        +"TOT_MIRAD_2012;"\
                                        +"TOT_MIRAD_2012_NODATA;")
                           
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
            if "Gage_no" in headers: idindex = headers.index("Gage_no")
            if "Gage_name" in headers: nmindex = headers.index("Gage_name")
            if "COMID" in headers: comIDindex = headers.index("COMID")
            if "Lat_snap" in headers: latindex = headers.index("Lat_snap")
            if "Long_snap" in headers: longindex = headers.index("Long_snap")
            #strip the header line
            file.pop(0)
            header =[]
            header.append("-+-+-+-+-+-+-+-+-+ NEW RUN -+-+-+-+-+-+-+-+-+")
            header.append("Execute Date: " + str(datetime.date.today()))
            header.append("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")                   
            header.append(",".join(['COMID','WorkspaceID','Description','LAT','LONG']+self._formatRow(params)))

            Shared.writeToFile(os.path.join(workingDir,config["outputFile"]),header)

            with FederalHighwayWrapper(workingDir, projectID) as fh:                
                for station in file:
                    results={'Values':[{}]}
                    try:
                        g = gage.gage(station[idindex],station[comIDindex],station[latindex],station[longindex],args.outwkid,station[nmindex].replace(",", " "))
                        results = fh.Run(g, params)  
                    
                        if results is None: results={'Values':[{}]}
                        Shared.appendLineToFile(os.path.join(workingDir,config["outputFile"]),",".join(str(v) for v in [g.comid,fh.workspaceID,results.Description,g.lat,g.long]+self._formatRow(results.Values,params)))
                    except:
                        tb = traceback.format_exc()
                        WiMLogging.sm("error computing gage "+g.id+" "+tb)
                        continue
                    finally:
                        #ensure gc has collected before next gage
                        gc.collect()
                #next station
            #endwith
        except:
            tb = traceback.format_exc()
            WiMLogging.sm("error running "+tb)

    def _formatRow(self, params, definedkeys =None):        
            r = []
            keys = params if not definedkeys else definedkeys
            for k in keys:
                for p_val in ['localvalue','totalvalue','globalvalue']:
                    value = str(k) + "_" + str(p_val) if not definedkeys else params[k][p_val] if k in params and p_val in params[k] else "not reported. see log file"
                    r.append(value)
                #next p_val
            #next p

            return r
    

if __name__ == '__main__':
    Main()