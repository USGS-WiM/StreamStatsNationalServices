#------------------------------------------------------------------------------
#----- SpatialOps.py ------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  John Wall - Ph.D. Student NC State University
#              Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  Contains reusable global spatial methods
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  An explaination of different overlay tools is provided by the
#                   link below.
#
#              See:
#                   https://blogs.esri.com/esri/arcgis/2012/10/12/comparingoverlaytools/
#
#      dates:   05 NOV 2016 jkn - Created / Date notation edited by jw
#               03 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
import shutil
import sys
import os
from os.path import split
import tempfile
import arcpy
from arcpy.sa import *
from arcpy import env
import traceback
import json
from  WiMLib import WiMLogging
from contextlib import contextmanager
import PrismOps
import numpy as np
#endregion

##-------1---------2---------3---------4---------5---------6---------7---------8
##       SpatialOps
##-------+---------+---------+---------+---------+---------+---------+---------+
class SpatialOps(object):
    #region Constructor
    def __init__(self, workspacePath):
        #public properties
        
        #protected properties
        self._WorkspaceDirectory = workspacePath
        self._TempLocation = tempfile.mkdtemp(dir=os.path.join(self._WorkspaceDirectory,"Temp"))  
        
        arcpy.env.workspace = self._TempLocation 
        arcpy.env.overwriteOutput = True
        self._sm("initialized spatialOps")
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            shutil.rmtree(self._TempLocation, True)

            arcpy.ResetEnvironments()
            arcpy.ClearEnvironment("workspace")
        except:
            self._sm("Failed to remove temp space on close","ERROR",50)
    
    #endregion 
    
    #region Feature methods 
    def Select(self, inFeature, intersectfeature, fields):
        arcpy.Intersect_analysis([inFeature,intersectfeature], "intersectOutput")
    def ProjectFeature(self, inFeature, sr):
        #http://joshwerts.com/blog/2015/09/10/arcpy-dot-project-in-memory-featureclass/
        inSR = None
        out_projected_fc = None
        path =""
        name =""
        source_curs = None
        ins_curs = None
        row = None
        try:
            inSR = arcpy.Describe(inFeature).spatialReference
            if (inSR.name == sr.name): return inFeature

            name = arcpy.Describe(inFeature).name +"_proj"
            
            out_projected_fc = arcpy.management.CreateFeatureclass(self._TempLocation, name,
                                                arcpy.Describe(inFeature).shapeType,
                                                template=inFeature,
                                                spatial_reference=sr)

            # specify copy of all fields from source to destination
            fields = ["Shape@"] + [f.name for f in arcpy.ListFields(inFeature) if not f.required]

            # project source geometries on the fly while inserting to destination featureclass
            with arcpy.da.SearchCursor(inFeature, fields, spatial_reference=sr) as source_curs,\
                arcpy.da.InsertCursor(out_projected_fc, fields) as ins_curs:
                for row in source_curs:
                    ins_curs.insertRow(row)
                #next
            #end with

            return out_projected_fc
        except:
            tb = traceback.format_exc()
            raise Exception("Failed to project feature " +tb)
        finally:
            inSR = None
            out_projected_fc= None
            path =""
            name =""
            if source_curs is not None: del source_curs
            if ins_curs is not None: del ins_curs
            if row is not None: del row
    def PersistFeature(self,inFeature, path, name):
        arcpy.FeatureClassToFeatureClass_conversion(inFeature,path,name)
    def getAreaSqMeter(self, inFeature):
        AreaValue = 0
        try:

            sr = arcpy.Describe(inFeature).spatialReference
            if(sr.type == "Geographic"):
                #USA_Contiguous_Albers_Equal_Area_Conic_USGS_version:
                inFeature = self.ProjectFeature(inFeature,arcpy.SpatialReference(102039))[0]
                sr = arcpy.Describe(inFeature).spatialReference

            cursor = arcpy.da.SearchCursor(inFeature, "SHAPE@")
            for row in cursor:
                AreaValue += row[0].area * sr.metersPerUnit * sr.metersPerUnit 
                
            return AreaValue if (AreaValue > 0) else None
        except:
            tb = traceback.format_exc()
            self._sm("Error computing area "+tb,"ERROR")
            return None 
    def spatialJoin(self, inFeature, maskfeature, fieldStr='',methodStr ='' ):
        mask = None
        fieldmappings = None
        try:
            sr = arcpy.Describe(inFeature).spatialReference
            mask = self.ProjectFeature(maskfeature,sr) 
            out_projected_fc = os.path.join(self._TempLocation, "ovrlytmpsj")
            
            if(fieldStr != '' and methodStr != ''):
                # Create a new fieldmappings and add the two input feature classes.
                fieldmappings = arcpy.FieldMappings()
                fieldmappings.addTable(mask)
                fieldmappings.addTable(inFeature)

                #for each field + method
                methods = [x.strip() for x in methodStr.split(';')]
                Fields = [x.strip() for x in fieldStr.split(';')]
                #sm(Fields.count + " Fields & " + methods.count + " Methods")
                for field in Fields:
                    fieldIndex = fieldmappings.findFieldMapIndex(field)
                    for method in methods:  
                        map = self.__getFieldMap(fieldmappings,fieldIndex,method+field,method)
                        if map is not None:
                            fieldmappings.addFieldMap(map)
                    #next method
                #next Field

            self._sm("performing spatial join ...")
            return arcpy.SpatialJoin_analysis(maskfeature, inFeature, out_projected_fc,'', '', fieldmappings,"COMPLETELY_CONTAINS")

        except:
            tb = traceback.format_exc()
            self._sm(tb,"Error",152)
        finally:
            mask = None
            #do not release
            out_projected_fc = None
    def spatialOverlay(self, inFeature, maskfeature, matchOption = "COMPLETELY_CONTAINS"):
        mask = None
        try:
            sr = arcpy.Describe(inFeature).spatialReference
            mask = self.ProjectFeature(maskfeature,sr) 
            out_projected_fc = os.path.join(self._TempLocation, "ovrlytmpso")

            self._sm("performing spatial join ...")
            return arcpy.SpatialJoin_analysis(maskfeature, inFeature, out_projected_fc,'JOIN_ONE_TO_MANY', 'KEEP_COMMON', None, matchOption)

        except:
            tb = traceback.format_exc()
            self._sm(tb,"Error",152)
        finally:
            mask = None 
            #do not release
            out_projected_fc = None      
    def getFeatureStatistic(self, inFeature, maskFeature, statisticRules, fieldStr, WhereClause = "", matchOption = "COMPLETELY_CONTAINS"):
        '''
        computes the statistic 
        Statistic rules, semicolon separated
                            SUM—Adds the total value for the specified field.
                            MEAN—Calculates the average for the specified field.
                            MIN—Finds the smallest value for all records of the specified field.
                            MAX—Finds the largest value for all records of the specified field.
                            RANGE—Finds the range of values (MAX minus MIN) for the specified field.
                            STD—Finds the standard deviation on values in the specified field.
                            COUNT—Finds the number of values included in statistical calculations.
                                This counts each value except null values. To determine the number
                                of null values in a field, use the COUNT statistic on the field in
                                question, and a COUNT statistic on a different field which does not 
                                contain nulls (for example, the OID if present), then subtract the two values.
                            FIRST—Finds the first record in the Input Table and uses its specified field value.
                            LAST—Finds the last record in the Input Table and uses its specified field value.
        '''
        map = []
        values = {}
        cursor = None
        tblevalue=None
        spOverlay = None
        try:            
            methods = [x.strip() for x in statisticRules.split(';')]
            Fields = [x.strip() for x in fieldStr.split(';')]
            #sm(Fields.count + " Fields & " + methods.count + " Methods")
            for field in Fields:
                for method in methods:  
                    map.append([field,method])
                #next method
            #next Field

            spOverlay = self.spatialOverlay(inFeature,maskFeature,matchOption)
            
            #Validate that we have values within the polygon/basin
            #   If we do not, set all values equal to zero
            if(int(arcpy.GetCount_management(spOverlay).getOutput(0)) < 1):
                self._sm("Basin contains no features", "WARNING")
                for m in map: values[m[0]]={m[1]: float(0)}
                return values
            #endif

            #If we do have values, then carry out spatial statistics
            tblevalue = arcpy.Statistics_analysis(spOverlay,os.path.join(self._TempLocation, "ftmp"),map)
            mappedFeilds = [x[1]+"_"+x[0] for x in map]
            whereClause = WhereClause
            self._sm("The WhereClause is: " + whereClause)
            cursor = arcpy.da.SearchCursor(tblevalue, mappedFeilds, whereClause)
            try:
                for row in cursor:
                    i=0
                    for m in map:
                        values[m[0]]={m[1]: float(row[i])}
                        i+=1
                return values
            #Is an except catch for when row contains nothing
            except:
                self._sm("Now rows were found in cursor. Setting values to zero.", "WARNING")
                for m in map: values[m[0]]={m[1]: float(0)}
                return values
        except:
            tb = traceback.format_exc()
            self._sm("Failed to get raster statistic " +tb,"ERROR",229)
        finally:
            #local cleanup
            if cursor is not None: del cursor; cursor = None            
            if tblevalue is not None: del tblevalue; tblevalue = None
            if spOverlay is not None: del spOverlay; spOverlay = None
    def getFeatureCount(self,inFeature, maskFeature):
        '''
        Finds the number of features
        '''
        try:            
            spOverlay = self.spatialOverlay(inFeature,maskFeature)
            val = int(arcpy.GetCount_management(spOverlay).getOutput(0)) 
            
            return val
        except:
            tb = traceback.format_exc()
            self._sm("Failed to get raster statistic " +tb,"ERROR",229)
        finally:
            #local cleanup
            if spOverlay is not None: del spOverlay; spOverlay = None                     
    #endregion

    #region Raster methods
    def setpRAE(self,snapgds, directory,extentgds = None, maskgds = None):
        """Set Raster Analysis Environment.
            snapgds: snap IGeodataset 
            directory: workspace and scratch workspace directory
            extentgds: extent IGeodataset
            maskgds: mask IGeodataset
        """
        try:
            raise Exception("This is a work in progress. Its not quite right yet")
            #https://pro.arcgis.com/en/pro-app/arcpy/classes/env.htm
        
            arcpy.ResetEnvironments()
            pExists = os.path.exists(directory)

            #set spatial reference
            if maskgds is not None:
                #arcpy.env.outputCoordinateSystem = arcpy.Describe(maskgds).spatialReference
                arcpy.env.extent = arcpy.Describe(maskgds).extent
                #arcpy.env.mask = maskgds
            else:
                arcpy.env.outputCoordinateSystem = arcpy.Describe(snapgds).spatialReference

            #endif

            #set ouput workspace - check exists first and make        
            if not pExists:
                #create one
                os.makedirs(directory)
            #endif
        
            arcpy.env.workspace = directory
            arcpy.env.scratchWorkspace = directory
        
            #Cell Size
            desc = arcpy.Describe(snapgds)
            arcpy.env.cellSize = snapgds
            #extent
            #if extentgds is not None:
                #arcpy.env.extent = extentgds
            arcpy.env.snapRaster = snapgds
        except:
            arcpy.ResetEnvironments()
            tb = traceback.format_exc()
            return
    def getValueAtCentroid(self, inFeature, inRaster):
        try:
            sr = arcpy.Describe(inRaster).spatialReference
            i=0
            totvalue = 0
            shapeName = arcpy.Describe(inFeature).shapeFieldName
            with arcpy.da.SearchCursor(inFeature, "SHAPE@", spatial_reference=sr) as source_curs:
                for row in source_curs:
                    i = i + 1
                    feature = row[0]
                    value = arcpy.GetCellValue_management(inRaster,str(feature.centroid.X) + ' ' + str(feature.centroid.Y)).getOutput(0)
                    totvalue = float(value)/i
            
            return totvalue
        except:
            tb = traceback.format_exc()
            self._sm("Failed to get raster at point " +tb,"ERROR",220)
            raise Exception("Failed to get raster at point " +tb)
    def getRasterStatistic(self,inRaster, maskFeature, statisticRule):
        '''
        computes the statistic 
        Statistic rules:    MINIMUM —Smallest value of all cells in the input raster.
                            MAXIMUM —Largest value of all cells in the input raster.
                            MEAN —Average of all cells in the input raster.
                            STD —Standard deviation of all cells in the input raster.
                            UNIQUEVALUECOUNT —Number of unique values in the input raster.
                            TOP —Top or YMax value of the extent.
                            LEFT —Left or XMin value of the extent.
                            RIGHT —Right or XMax value of the extent.
                            BOTTOM —Bottom or YMin value of the extent.
                            CELLSIZEX —Cell size in the x-direction.
                            CELLSIZEY —Cell size in the y-direction.
                            VALUETYPE —Type of the cell value in the input raster:
                                        0 = 1-bit
                                        1 = 2-bit
                                        2 = 4-bit
                                        3 = 8-bit unsigned integer
                                        4 = 8-bit signed integer
                                        5 = 16-bit unsigned integer
                                        6 = 16-bit signed integer
                                        7 = 32-bit unsigned integer
                                        8 = 32-bit signed integer
                                        9 = 32-bit floating point
                                        10 = 64-bit double precision
                                        11 = 8-bit complex
                                        12 = 16-bit complex
                                        13 = 32-bit complex
                                        14 = 64-bit complex
                            COLUMNCOUNT —Number of columns in the input raster.
                            ROWCOUNT —Number of rows in the input raster.
                            BANDCOUNT —Number of bands in the input raster.
                            ANYNODATA —Returns whether there is NoData in the raster.
                            ALLNODATA —Returns whether all the pixels are NoData. This is the same as ISNULL.
                            SENSORNAME —Name of the sensor.
                            PRODUCTNAME —Product name related to the sensor.
                            ACQUISITIONDATE —Date that the data was captured.
                            SOURCETYPE —Source type.
                            CLOUDCOVER —Amount of cloud cover as a percentage.
                            SUNAZIMUTH —Sun azimuth, in degrees.
                            SUNELEVATION —Sun elevation, in degrees.
                            SENSORAZIMUTH —Sensor azimuth, in degrees.
                            SENSORELEVATION —Sensor elevation, in degrees.
                            OFFNADIR —Off-nadir angle, in degrees.
                            WAVELENGTH —Wavelength range of the band, in nanometers.
        '''
        outExtractByMask = None
        try:
            arcpy.env.cellSize = "MINOF"
            sr = arcpy.Describe(inRaster).spatialReference
            mask = self.ProjectFeature(maskFeature,sr) 
            self._LicenseManager("Spatial")
            outExtractByMask = arcpy.sa.ExtractByMask(inRaster, mask)
            value = arcpy.GetRasterProperties_management(outExtractByMask, statisticRule)
            cellsize = float(arcpy.GetRasterProperties_management(inRaster, 'CELLSIZEX').getOutput(0))**2 # -- Added by JWX from below.
            return float(value.getOutput(0))
        except:
            tb = traceback.format_exc()
            self._sm("WARNING: Failed to get raster statistic computing centroid value.","WARNING",229)
            cellsize = float(arcpy.GetRasterProperties_management(inRaster, 'CELLSIZEX').getOutput(0))**2
            self._sm("Raster cell size: " + str(cellsize) , "WARNING")
            maskArea = self.getAreaSqMeter(self.mask)
            maskArea = maskArea*0.000001
            centValue = self.getValueAtCentroid(maskFeature,inRaster)            # try getting centroid
            if centValue in ['NaN', 'none', 0]:
                self._sm("WARNING: Raster statistic AND get value at centroid failed. Results likely erroneous.","WARNING")
            return ((maskArea/cellsize)*centValue)*cellsize #Added cellsize multiplier -- JWX
        finally:
            outExtractByMask = None           
            mask = None
            if sr is not None: del sr; sr = None
            self._LicenseManager("Spatial",False)       
            
    def getPrismStatistic(self,inRaster, maskFeature, statisticRules, timeRange, timeMethod, dataPath):
        '''
        computes the statistic 
        Statistic rules:    MINIMUM —Smallest value of all cells in the input raster.
                            MAXIMUM —Largest value of all cells in the input raster.
                            MEAN —Average of all cells in the input raster.
                            STD —Standard deviation of all cells in the input raster.
                            UNIQUEVALUECOUNT —Number of unique values in the input raster.
                            TOP —Top or YMax value of the extent.
                            LEFT —Left or XMin value of the extent.
                            RIGHT —Right or XMax value of the extent.
                            BOTTOM —Bottom or YMin value of the extent.
                            CELLSIZEX —Cell size in the x-direction.
                            CELLSIZEY —Cell size in the y-direction.
                            VALUETYPE —Type of the cell value in the input raster:
                                        0 = 1-bit
                                        1 = 2-bit
                                        2 = 4-bit
                                        3 = 8-bit unsigned integer
                                        4 = 8-bit signed integer
                                        5 = 16-bit unsigned integer
                                        6 = 16-bit signed integer
                                        7 = 32-bit unsigned integer
                                        8 = 32-bit signed integer
                                        9 = 32-bit floating point
                                        10 = 64-bit double precision
                                        11 = 8-bit complex
                                        12 = 16-bit complex
                                        13 = 32-bit complex
                                        14 = 64-bit complex
                            COLUMNCOUNT —Number of columns in the input raster.
                            ROWCOUNT —Number of rows in the input raster.
                            BANDCOUNT —Number of bands in the input raster.
                            ANYNODATA —Returns whether there is NoData in the raster.
                            ALLNODATA —Returns whether all the pixels are NoData. This is the same as ISNULL.
                        Perhaps not relevant in this case
                        #                             SENSORNAME —Name of the sensor.
                        #                             PRODUCTNAME —Product name related to the sensor.
                        #                             ACQUISITIONDATE —Date that the data was captured.
                        #                             SOURCETYPE —Source type.
                        #                             CLOUDCOVER —Amount of cloud cover as a percentage.
                        #                             SUNAZIMUTH —Sun azimuth, in degrees.
                        #                             SUNELEVATION —Sun elevation, in degrees.
                        #                             SENSORAZIMUTH —Sensor azimuth, in degrees.
                        #                             SENSORELEVATION —Sensor elevation, in degrees.
                        #                             OFFNADIR —Off-nadir angle, in degrees.
                        #                             WAVELENGTH —Wavelength range of the band, in nanometers.
        '''
        
        try:
            arcpy.env.cellSize = "MINOF"
            sr = arcpy.Describe(inRaster).spatialReference
            mask = self.ProjectFeature(maskFeature,sr) 
            self._LicenseManager("Spatial")
            
            outExtractByMask = arcpy.sa.ExtractByMask(inRaster, mask)
            
            rules = ['MINIMUM', 'MAXIMUM','MEAN','STD','UNIQUEVALUECOUNT', 'SUM']
            statisticRules = [x.upper() for x in statisticRules.split(';')]
            computation = np.all([x in rules for x in statisticRules])
            
            if computation == True:
                rasterCellIdx = arcpy.RasterToNumPyArray(outExtractByMask, nodata_to_value = -9999.00)
                return float(PrismOps.get_statistic(rasterCellIdx, dataPath, statisticRules,
                                                    timeRange, timeMethod))
            else:
                value = arcpy.GetRasterProperties_management(outExtractByMask, statisticRules[0])
                return float(value.getOutput(0))
          
        except:
            tb = traceback.format_exc()
            self._sm("Failed to get raster statistic " +tb,"ERROR",229)
            cellsize = float(arcpy.GetRasterProperties_management(inRaster, 'CELLSIZEX').getOutput(0))**2
            self._sm("Raster cell size: " + str(cellsize) , "ERROR")
            # try getting centroid
            return self.getValueAtCentroid(maskFeature,inRaster)
        finally:
            outExtractByMask = None           
            mask = None
            if sr is not None: del sr; sr = None
            self._LicenseManager("Spatial",False)
                        
    def getRasterPercentAreas(self,inRaster, maskFeature, uniqueRasterIDfield='VALUE',rasterValueField='COUNT'):
        '''
        computes the statistic 
        '''
        results ={}
        try:
            arcpy.env.cellSize = "MINOF"
            arcpy.env.overwriteOutput = True
            #define land use key value dictionary with all possible values
            for row in arcpy.da.SearchCursor(inRaster, uniqueRasterIDfield):
                results[str(row[0])] = 0
            #next row

            #make maskRaster
            outExtractByMask = arcpy.sa.ExtractByMask(inRaster, maskFeature)
            #arcpy.BuildRasterAttributeTable_management(outExtractByMask, "Overwrite")
            rows = arcpy.SearchCursor(outExtractByMask, "", "", "VALUE; COUNT")
            for row in rows:
                v = row.getValue("VALUE")  
                c = row.getValue("COUNT")  
                print v,c

            ##get total cell count for percent area computation
            #field = arcpy.da.TableToNumPyArray('in_memory/mask.img', rasterValueField, skip_nulls=True)
            #sum = field[rasterValueField].sum() 

            #loop over masked raster rows
            for row in arcpy.da.SearchCursor('in_memory/mask123.img', [uniqueRasterIDfield, rasterValueField] ):
                #get values
                value, count = row
                percentArea = float(count)
                results[str(row[0])] = percentArea
            #next row
            
        except:
            tb = traceback.format_exc()
            self._sm("Error computing Raster Percent Area " +tb,"ERROR",289)
                    
        return results
    
    def getRasterPercent(self,inRaster, maskFeature, ClassificationCodes=None, uniqueRasterIDfield='VALUE',rasterValueField='COUNT'):
        '''
        computes the raster % statistic 
        classificationCodes = comma separated classification ID's
        rCode is the classification requested code[s] as comma separated string
        '''
        attField = None    
        attExtract = None   
        constfield = None
        const1 = None
        mask = None
        sr = None
        try:
            sr = arcpy.Describe(inRaster).spatialReference
            mask = self.ProjectFeature(maskFeature,sr)        

            arcpy.env.cellSize = inRaster
            arcpy.env.snapRaster = inRaster
            try:
                arcpy.env.mask = mask
            except:
                self._LicenseManager("Spatial")
                outExtractByMask = ExtractByMask(inRaster, mask)
                arcpy.env.mask = outExtractByMask
                self._LicenseManager("Spatial", False)
            
            arcpy.env.extent = arcpy.Describe(mask).extent
            arcpy.env.outputCoordinateSystem = sr
            # Check out the ArcGIS Spatial Analyst extension license
            self._LicenseManager("Spatial")
            #creates a constant of the enviroment
            const1 = arcpy.sa.CreateConstantRaster(1)
            const1.save(os.path.join(self._TempLocation,"const1.img"))
            constfield = arcpy.da.TableToNumPyArray(os.path.join(self._TempLocation,"const1.img"), rasterValueField, skip_nulls=True)

            totalCount = float(constfield[rasterValueField].sum())
            if ClassificationCodes is not None:
                SQLClause = " OR ".join(map(lambda s: uniqueRasterIDfield +"=" + s,ClassificationCodes.strip().split(",")))
            else:
                SQLClause = "VALUE > 0"

            # Execute ExtractByAttributes
            #ensure spatial analyst is checked out
            attExtract = arcpy.sa.ExtractByAttributes(inRaster, SQLClause)  
            #must save raster
            unique_name_img = arcpy.CreateUniqueName(os.path.join(self._TempLocation, "xxx.img"))
            attExtract.save(unique_name_img)
            if self.isRasterALLNoData(attExtract): return float(0)
            #Does not respect the workspace dir, so need to set it explicitly
            attField = arcpy.da.TableToNumPyArray(unique_name_img, rasterValueField, skip_nulls=True) #I assume I should use the same variable over, but it's unclear to me -- JWX          
            results  = (float(attField[rasterValueField].sum())/totalCount)*100 #For a percentage the result should be multiplied by 100 -- JWX
            
        except:
            tb = traceback.format_exc()
            self._sm("Error computing Raster Percent Area " +tb,"ERROR",289)
            return self.getValueAtCentroid(mask, inRaster)
        finally:
            #local clean up
            if attField is not None: del attField; attField = None    
            attExtract = None   
            if constfield is not None: del constfield; constfield = None
            const1 = None
            mask = None
            if sr is not None: del sr; sr = None
            self._LicenseManager("Spatial",False) 
               
        return results
    def isRasterALLNoData(self,inRaster):
        try:
            #isNull method returns 1 if the input value is NoData, and 0 if not
            
            if inRaster.maximum is None and inRaster.minimum is None: return True
            else: return False;
        except:
            tb = traceback.format_exc()
            self._sm("Error computing Raster Percent Area " +tb,"ERROR",289)
            return True
    #endregion

    #region helper methods
    def _LicenseManager(self, extension, checkout=True):
        v = None
        licAvailability = arcpy.CheckExtension(extension)
        if(licAvailability == "Available"): 
            if(checkout):v = arcpy.CheckOutExtension(extension)
            else: v= arcpy.CheckInExtension(extension)
        else:raise Exception("Lisense "+ extension +" "+ licAvailability)
        
        print v
    def __getFieldMap(self, mappedFields,FieldIndex, newName, mergeRule):
        '''
        Maps the field
        Merge rules: 
            First	The first source value.
            Last	The last source value.
            Join	A concatenation of source values. You can use a delimiter to separate multiple input values.
            Sum     The sum total of all source values.
            Mean	The mean (average) of all source values.
            Median	The median (middle) of all source values.
            Mode	The source value that is the most common or has the highest frequency.
            Min	The minimum (lowest) source value.
            Max	The maximum (highest) source value.
            Standard deviation	The standard deviation of all source values.
            Count	The number of source values, excluding null values.
            Range	The absolute difference between the minimum and maximum source values.
        '''

        try:
            fieldmap = mappedFields.getFieldMap(FieldIndex)
            # Get the output field's properties as a field object
            field = fieldmap.outputField

            # Rename the field and pass the updated field object back into the field map
            field.name = newName
            field.aliasName = newName

            fieldmap.outputField = field
            fieldmap.mergeRule = mergeRule

            return fieldmap
        except:
            tb = traceback.format_exc()
            self._sm(tb+ " Failed to map "+ newName)
            return None
    def _sm(self,msg,type="INFO", errorID=0):        
        WiMLogging.sm(msg,type="INFO", errorID=0)
    #endregion