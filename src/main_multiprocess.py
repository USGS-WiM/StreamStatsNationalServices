# ------------------------------------------------------------------------------
# ----- Main_Multiprocess.py -----------------------------------------------
# ------------------------------------------------------------------------------
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
# discussion: In windows machines, in order to fork a new process it has to be in the main module
#
# ------------------------------------------------------------------------------

# region "Imports"
import sys
import numpy as np
import gc
import arcpy  # Left in so that arcpy does not have to be loaded more than once for child processes
import multiprocessing as mp
import os
import datetime
import argparse
import json
import traceback
import string
import time
from FederalHighwayWrapper.FederalHighwayWrapper import FederalHighwayWrapper
from Resources import gage

from WIMLib import Shared
from WIMLib import WiMLogging
from WIMLib.Config import Config


# endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Main mulitprocess
##-------+---------+---------+---------+---------+---------+---------+---------+

def _run(projectID, infile, outwkid, parameters, arr, start_idx, end_idx):


        config = Config(json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'))))

        if projectID == '#' or not projectID:
            raise Exception('Input Study Area required')

        workingDir = Shared.GetWorkspaceDirectory(config["workingdirectory"], projectID)

        WiMLogging.init(os.path.join(workingDir, "Temp"), "gage.log")
        WiMLogging.sm("Starting routine")
        params = parameters.split(";") if (parameters) else config["characteristics"].keys()


        file = Shared.readCSVFile(infile)
        headers = file[0]
        if "Gage_no" in headers: idindex = headers.index("Gage_no")
        if "Gage_name" in headers: nmindex = headers.index("Gage_name")
        if "COMID" in headers: comIDindex = headers.index("COMID")
        if "Lat_snap" in headers: latindex = headers.index("Lat_snap")
        if "Long_snap" in headers: longindex = headers.index("Long_snap")
        # strip the header line
        file.pop(0)
        header = []
        header.append("-+-+-+-+-+-+-+-+-+ NEW RUN -+-+-+-+-+-+-+-+-+")
        header.append("Execute Date: " + str(datetime.date.today()))
        header.append("-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

        header.append(
            ",".join(['COMID', 'WorkspaceID', 'Description', 'LAT', 'LONG', 'STATE'] + _formatRow(params)))

        Shared.writeToFile(os.path.join(workingDir, config["outputFile"]), header)

        gagelist = file[start_idx:end_idx]

        with FederalHighwayWrapper(workingDir, projectID) as fh:

            x = start_idx
            for station in gagelist:
                # Create temp directory so ARC does not run out of internal memory
                newTempDir = r"D:\Applications\output\gage_iii\temp\gptmpenvr_" + time.strftime(
                    '%Y%m%d%H%M%S') + '2018' + str(
                    x)
                os.mkdir(newTempDir)
                os.environ["TEMP"] = newTempDir
                os.environ["TMP"] = newTempDir
                results = {'Values': [{}]}

                g = gage.gage(station[idindex], station[comIDindex], station[latindex], station[longindex],
                              outwkid, station[nmindex], '', station[stateindex])
                station[idindex], station[comIDindex], station[latindex], station[longindex], sr, station[nmindex], '', \
                station[stateindex]
                results = fh.Run(g, params)
                print results

                if results is None: results = {'Values': [{}]}
                Shared.appendLineToFile(os.path.join(workingDir, config["outputFile"]), ",".join(str(v) for v in
                                                                                                 [g.comid,
                                                                                                  fh.workspaceID,
                                                                                                  results.Description,
                                                                                                  g.lat,
                                                                                                  g.long,
                                                                                                  g.state] + _formatRow(
                                                                                                     results.Values,
                                                                                                     params)))

                gc.collect()
                x += 1
            # next station
        # endwith



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
    parser = argparse.ArgumentParser()
    parser.add_argument("-projectID", help="specifies the projectID", type=str, default="FH")
    parser.add_argument("-file",
                        help="specifies csv file location including gage lat/long and comid's to estimate",
                        type=str,
                        default=r'D:\Applications\input\gagesiii_lat_lon.csv')
    parser.add_argument("-outwkid", help="specifies the esri well known id of pourpoint ", type=int,
                        default='4326')
    parser.add_argument("-parameters", help="specifies the ';' separated list of parameters to be computed",
                        type=str,
                        default="TOT_NID_DISTURBANCE_INDEX")
    args = parser.parse_args()

    processing_objects = []
    split = 1
    gage_no = range(17000)
    # Array used for concurrency locks
    arr = mp.Array('c', 1000)
    split_idxs = np.array_split(gage_no, split)
    processes = []

    #ACTUAL MULTIPROCESSING PART --------------------------------------
    # for x in range(len(split_idxs)):
    #
    #     p = mp.Process(target=_run, args=[args.projectID+str(x),
    #                                                 args.file,
    #                                                 args.outwkid,
    #                                                 args.parameters,
    #                                                 arr,
    #                                                 split_idxs[x][0],
    #                                                 split_idxs[x][-1]])
    #     # Add process to list
    #     processes.append(p)
    #     p.start()
    #---------------------------------------------------------------------

    # DEBUG in SERIAL, to remove ------------------------------------------
    x = 0
    _run(args.projectID+str(x),
        args.file,
        args.outwkid,
        args.parameters,
        arr,
        split_idxs[x][0],
        split_idxs[x][-1])
    #--------------------------------------------------------------------------