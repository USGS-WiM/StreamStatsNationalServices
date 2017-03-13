#------------------------------------------------------------------------------
#----- Logging.py ----------------------------------------------------
#------------------------------------------------------------------------------

#-------1---------2---------3---------4---------5---------6---------7---------8
#       01234567890123456789012345678901234567890123456789012345678901234567890
#-------+---------+---------+---------+---------+---------+---------+---------+

# copyright:   2016 WiM - USGS

#    authors:  Jeremy K. Newson USGS Web Informatics and Mapping
# 
#   purpose:  Simple log tracking app.
#          
#discussion:  
#

#region "Comments"
#11.05.2014 jkn - Created
#endregion

#region "Imports"
import os
import logging
#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       Logging
##-------+---------+---------+---------+---------+---------+---------+---------+
#region Constructor
LogMessages =[]
""" Handles logging  """
def init(logpath, fileName):  
    if not os.path.exists(logpath):
        os.makedirs(logpath)
         
    logdir = os.path.join(logpath, fileName)
    logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)

def sm(msg, type="INFO", errorID=0):
    LogMessages.append(type +':' + msg.replace('_',' '))
    print(type +' ' + str(errorID) + ' ' + msg)
    if type in ('ERROR'): logging.error(str(errorID) +' ' + msg)
    else : logging.info(msg)


