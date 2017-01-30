class gage(object):
    """description of class"""
    def __init__(self,id, comid, lat,long, spatialref, name, descr = ""):
        self.id = id
        self.name = name
        self.comid = comid
        self.lat = lat
        self.long = long
        self.sr = spatialref
        self.description = descr

