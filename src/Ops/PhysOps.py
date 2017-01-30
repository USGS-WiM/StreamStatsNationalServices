#------------------------------------------------------------------------------
#----- AnthOps.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  PhysProps is a server class, PhysProps provides a combination of useful 
#               physiographic functions and properties. 
#          
#     usage:  calculating % LandCoverage or other enviromnetal pollution orginating from human activity
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
import WiMLib.Shared
from WiMLib.MapLayer import *

#endregion

class PhysOps(SpatialOps):
    #region Constructor and Dispose
    def __init__(self, workspacePath):     
        #initialize logging
        SpatialOps.__init__(self, workspacePath) 
        self.WorkspaceID = os.path.basename(os.path.normpath(workspacePath))
         
        self._sm("initialized PhysOps")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SpatialOps.__exit__(self, exc_type, exc_value, traceback)  

    #endregion 

    #region Methods 
              
    #endregion  
      
    #region Helper Methods

    #endregion    