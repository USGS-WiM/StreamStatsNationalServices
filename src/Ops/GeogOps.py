#------------------------------------------------------------------------------
#----- GeogOps.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  GeogProps is a server class, GeogOps provides a combination of useful
#               geographic functions and properties  
#          
#     usage:  
#             
#
#discussion:  
#       

#region "Comments"
#11.30.2016 jkn - Created
#endregion

#region "Imports"
import traceback
import tempfile
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import json
from  WiMLib.SpatialOps import SpatialOps
from WiMLib.Resources import *
from WiMLib.MapLayer import *

#endregion

class GeogOps(SpatialOps):
    #region Constructor
    def __init__(self, workspacePath):     
        SpatialOps.__init__(self, workspacePath) 
        self.WorkspaceID = os.path.basename(os.path.normpath(workspacePath))

        self._sm("initialized GeogOps")
    #endregion 
    #region Methods 
               
    #endregion  
      
    #region Helper Methods

    #endregion       