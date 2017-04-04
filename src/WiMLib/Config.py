#------------------------------------------------------------------------------
#----- Config.py --------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Handles configuration of StreamStats
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  Singlton class that can only be instanciated once
#
#      dates:   01 DEC 2016 jkn - Created / Date notation edited by jw
#               03 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
#endregion
class Config:
    class __Config:
        def __init__(self, configurationitems = None):
            self.Items = configurationitems
    instance = None
    def __init__(self, configurationitems = None):
        if not Config.instance:
            if(configurationitems == None): raise Exception("you must specify a configuration object initially")
            Config.instance = Config.__Config(configurationitems)
        
    def __getattr__(self, name):
        try:
            return getattr(self.instance.Items, name)
        except:
            return None

    def getElement(self, elementName):
        items = self.instance.Items
        return items[elementName]
