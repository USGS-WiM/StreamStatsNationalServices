#intensionally left blank
# import arcpy
# 
# # with arcpy.da.SearchCursor(r'C:\Users\gpetrochenkov\Downloads\Wolock_prism-20171206T165217Z-001\Wolock_prism\basegrid\basegrid\prismidgdd',
# #                               ['Value']) as cursor:
# #     
# #     id=0
# #     for row in cursor:
# #         id += 1
# #         if id > 5:
# #             break
# #         print row
# 
# ras = arcpy.Raster(
    
    
# outExtractByMask = ExtractByMask("Rast", "mask.shp"))

import requests
import json

data = requests.get('https://cida.usgs.gov//nldi/comid/3923/tot')


chars = [str(x['characteristic_id']) for x in data.json()['characteristics']]

parameters = ["TOT_FRESHWATER_WD",
              "TOT_FRESHWATER_WD_NODATA" ,
            "TOT_IMPV11" ,
            "TOT_IMPV11_NODATA",
            "TOT_MIRAD_2012",
            "TOT_MIRAD_2012_NODATA",
            "TOT_NID_STORAGE_2013",
            "TOT_NID_STORAGE_2013_NODATA",
            "TOT_NORM_STORAGE_2013",
            "TOT_NORM_STORAGE_2013_NODATA",
            "TOT_DITCHES92",
            "TOT_DITCHES92_NODATA",
            "TOT_NPDES_MAJ_DENS",
            "TOT_NPDES_MAJ_DENS_NODATA",
            "TOT_NWALT12_41",
            "TOT_NWALT12_41_NODATA",
            "TOT_PPT7100_ANN"]

for x in parameters:
    if x not in chars:
        print x + ' not found'
   

# for x in data.json()['characteristics']:
#     print x