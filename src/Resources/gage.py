#------------------------------------------------------------------------------
#----- gage.py ----------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  THIS SECTION NEEDS TO BE UPDATED
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:  THIS SECTION NEEDS TO BE UPDATED
#
#------------------------------------------------------------------------------

class gage(object):
    """description of class"""
    def __init__(self,id, comid, lat,long, spatialref, name, descr = "", state=""):
        self.id = id
        self.name = name
        self.comid = comid
        self.lat = lat
        self.long = long
        self.sr = spatialref
        self.description = descr
        self.state = state

