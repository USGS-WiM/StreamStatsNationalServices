#------------------------------------------------------------------------------
#----- Config.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  handles configuration
#          
#discussion:  Singlton class that can only be instanciated once
#       

#region "Comments"
#12.1.2016 jkn - Created
#endregion

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
