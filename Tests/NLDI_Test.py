import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ServiceAgents.NLDIServiceAgent import NLDIServiceAgent
from WIMLib.Config import Config
import traceback
import json

class NLDI_Test(unittest.TestCase):
    def test_LocalBasin(self):
        result = None
        try:
            Config({"NLDIService": "https://cida.usgs.gov",
                              "queryParams": {
                                "nldiQuery": "https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/{0}/basin",
                                "nldiWFS": "/nwc/geoserver/nhdplus/ows?service=wfs&version=1.0.0&request=GetFeature&typeName=nhdplus:catchmentsp&srsName=EPSG:{0}&outputFormat=json&filter=<Filter xmlns=\"http://www.opengis.net/ogc\" xmlns:gml=\"http://www.opengis.net/gml\"><Contains><PropertyName>the_geom</PropertyName><gml:Point srsName=\"EPSG:{0}\"><gml:coordinates>{1},{2}</gml:coordinates></gml:Point></Contains></Filter>"
                              }}) 
            with NLDIServiceAgent() as sa:
                basin = sa.getBasin(None, True, -107.4698603, 44.78392464, 4326)
                result = json.dumps(basin)

            self.assertFalse(result == None or result =='')
        except:
            tb = traceback.format_exc()            
            self.fail(tb)

    def test_globalBasin(self):
        result = None
        try:
            Config({"NLDIService": "https://cida.usgs.gov",
                    "queryParams": {
                    "nldiQuery": "https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/{0}/basin",
                    "nldiWFS": "/nwc/geoserver/nhdplus/ows?service=wfs&version=1.0.0&request=GetFeature&typeName=nhdplus:catchmentsp&srsName=EPSG:{0}&outputFormat=json&filter=<Filter xmlns=\"http://www.opengis.net/ogc\" xmlns:gml=\"http://www.opengis.net/gml\"><Contains><PropertyName>the_geom</PropertyName><gml:Point srsName=\"EPSG:{0}\"><gml:coordinates>{1},{2}</gml:coordinates></gml:Point></Contains></Filter>"
                    }}) 
            with NLDIServiceAgent() as sa:
                basin = sa.getBasin(5335813, False)

                result = json.dumps(basin)
            self.assertFalse(result==None or result == '')
        except:
            tb = traceback.format_exc()
            self.fail(tb)

