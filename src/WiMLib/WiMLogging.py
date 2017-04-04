#------------------------------------------------------------------------------
#----- Logging.py ------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  A simple log tracking application for StreamStats.
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:   05 NOV 2016 jkn - Created / Date notation edited by jw
#               04 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
import os
import logging
#endregion

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


