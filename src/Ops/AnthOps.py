#------------------------------------------------------------------------------
#----- AnthOps.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  AnthOps is a server class, AnthOps provides a combination of useful
#               anthropogenic functions and properties 
#          
#     usage:  calculating % LandCoverage or other enviromnetal characteristics orginating from human activity
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
from  WiMLib import Shared
from WiMLib.MapLayer import *

#endregion

class AnthOps(SpatialOps):
