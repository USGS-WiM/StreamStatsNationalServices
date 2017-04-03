'''
Helper class to read and write geojson objects in ArcGIS as a replacement for
the arcpy.asShape(geojson) function. Requires ArcGIS installation...

Creation includes creating a geojson object from an ArcGIS feature class,
feature or geometry.

Reading is more complex. This module includes support for Feature Collections,
Features and Geometry. All geometry types are supported except for
GeometryCollection which is unsupported by ArcGIS. Feature collections must have
the same geometry type.

CRS support is included, but only for EPSG codes at this point (if the epsg code
is in the projection string we search for it with regex "epsg:\d\d\d\d\d?"

Motivation for this module came from the lack of ESRI support for geojson. As it
currently stands geometries created in ArcGIS without a projection are rounded
to three decimal places

@author: om_henners
'''

import arcpy
import os
import json
import tempfile
import copy
import shutil
import logging
from contextlib import contextmanager

logger = logging.getLogger("GIS.%s" % __name__)

@contextmanager
def _fc_insert_row(fc, spatial_ref=None):
    try:
        assert arcpy.Exists(fc), "%s does not Exist!" % fc
        logger.debug("Creating insert cursor on %s" % fc)
        rows = arcpy.InsertCursor(fc, spatial_ref)
        row = rows.newRow()
        yield row
        logger.debug("Inserting row")
        rows.insertRow(row)
        del row
        del rows
    except Exception, e:
        logger.error(e)
        raise e


def _get_point(pnt, sr=None):
    """
    Createa an arcpy Point object from a list of x, y, [z], [whatever]. The
    GeoJSON spec spports Z values but nothing else (assuming you want to
    implement that yourself) so we will do the same.

    Ref: http://geojson.org/geojson-spec.html#id13
    """
    geom = arcpy.Point()
    print pnt
    [geom.X, geom.Y,] = pnt[:2] #will return the entire array if there are only two coordinates
    if len(pnt) > 2:
        ##according to the spec, points must be x, y, [z], [whatever else]
        ##we will support Z values, but no others
        geom.Z = pnt[3]
    return geom


def _get_array(coords):
    """
    Return an arcpy.Array() object based on an input GeoJSON coordinates list.
    """
    array_obj = arcpy.Array()
    #print type(coords[0])
    for pnt in coords:
        geom = _get_point(pnt)
        array_obj.add(geom)
    return array_obj


def _read_point(geojson_coords, sr):
    geom = arcpy.PointGeometry(_get_point(geojson_coords), sr)
    return geom, "point"


def _read_multipoint(geojson_coords, sr):
    geom = arcpy.Multipoint(_get_array(geojson_coords), sr)
    return geom, "multipoint"


def _read_linestring(geojson_coords, sr):
    geom = arcpy.Polyline(_get_array(geojson_coords), sr)
    return geom, "polyline"


def _read_multilinestring(geojson_coords, sr):
    array_obj = arcpy.Array()
    for coords in geojson_coords:
        array_obj.add(_get_array(coords))
    geom = arcpy.Polyline(array_obj, sr)
    return geom, "polyline"


def _read_polygon(geojson_coords, sr):
    #weirdly, holes are separated in polygons as null point values in the
    #array - see http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//002z0000001t000000
    #on output only though - apparently in a multipart polygon arcpy does not
    #support cooincident polys - probably reasonable
    array_obj = arcpy.Array()
    for coords in geojson_coords:
        array_obj.add(_get_array(coords))
    geom = arcpy.Polygon(array_obj, sr)
    return geom, "polygon"


def _read_multipolygon(geojson_coords, sr):
    #AFAIK ArcGIS doesn't actually support the creation of multipart polygons
    #from the command line. So instead, return a set of polygons to be
    #processed individually.
    #Therefore we will return a set of geometries, and
    logger.debug("Reading multipolygon")
    geom_list = []
    for poly in geojson_coords:
        poly_obj = arcpy.Array()
        for coords in poly:
            poly_obj.add(_get_array(coords))
        geom_list.append(arcpy.Polygon(poly_obj, sr))
    geom = _dissolve_multipart(geom_list)
    return geom, "polygon"


def _dissolve_multipart(geom_list):
    folder = tempfile.mkdtemp()

    shape_list = []
    for geom in geom_list:
        unique_name = arcpy.CreateUniqueName(os.path.join(folder, "xxx.shp"))
        arcpy.CopyFeatures_management(geom, unique_name)
        shape_list.append(unique_name)

    merge_file = arcpy.CreateUniqueName(os.path.join(folder, "xxx.shp"))
    arcpy.Merge_management(shape_list, merge_file)
    dissolve_file = arcpy.CreateUniqueName(os.path.join(folder, "xxx.shp"))

    arcpy.Dissolve_management(merge_file, dissolve_file)
    out_poly = None
    for row in arcpy.SearchCursor(dissolve_file):
        out_poly = copy.copy(row.SHAPE)
        break

    try:
        shutil.rmtree(folder, True)
    except Exception, e:
        logging.critical(e)
        logging.critical("Couldn't delete folder %s" % folder)

    return out_poly


def _create_arcpy_sr(geojson_crs):
    """
    Creates an arcpy Spatial Reference object from incoming geojson crs string.
    """
    ##to do: Support more than EPSG. Thus this will need a re-write at some point -- changed by jwx
    assert "type" in geojson_crs, "GeoJSON does not validate.\n\t'type' missing from 'crs'"
    assert "properties" in geojson_crs, "GeoJSON does not validate.\n\t'properties' missing from 'crs'"
    assert geojson_crs["type"] == "name", "GeoJSON does not validate.\n\tOnly CRS type of name currently supported"
    assert "name" in geojson_crs["properties"], "GeoJSON does not validate.\n\t'name' missing from 'crs/properties'"

    epsg = geojson_crs["properties"]["name"].lower()
    assert epsg.startswith("epsg:"), "Only EPSG codes are supported for features so far"

    sr = arcpy.SpatialReference()
    sr.factoryCode = int(epsg.lstrip("epsg:"))
    sr.create()
    return sr


def read_geometry(geojson_geom, sr=None):
    """
    Creates an arcpy geometry object from a GeoJSON geometry object. This
    function is the closest mimic of the arcpy.AsShape function.

    Return ESRI geometry object.
    """
    logger.debug("Getting geometry")
    geojson_geom = dict([[k.lower(), v] for (k, v) in geojson_geom.iteritems()])
#    print geojson_geom
    assert geojson_geom["type"].lower() in ["point", "polygon", "linestring", "multipoint", "multilinestring", "multipolygon"], "GeoJSON geometry type invalid (%s)" % geojson_geom["type"]
    geojson_geom["type"] = geojson_geom["type"].lower()

    if(geojson_geom["type"] =="point"): return _read_point(geojson_geom["coordinates"], sr)
    elif(geojson_geom["type"] == "multipoint"): return _read_multipoint(geojson_geom["coordinates"], sr)
    elif(geojson_geom["type"] == "linestring"): return _read_linestring(geojson_geom["coordinates"], sr)
    elif(geojson_geom["type"] == "multilinestring"): return _read_multilinestring(geojson_geom["coordinates"], sr)
    elif(geojson_geom["type"] == "polygon"): return _read_polygon(geojson_geom["coordinates"], sr)
    elif(geojson_geom["type"] == "multipolygon"): return _read_multipolygon(geojson_geom["coordinates"], sr)



def read_feature(geojson_feat, target_fc, sr=None):
    """
    Takes a complete geojson feature (with optional CRS and attributes) and
    inserts the feature into the given feature class.

    In addition to the GeoJSON object specification, the assumption made is
    that feature attributes are stored within a key/value pair as an object
    named 'properties'.

    FC names are based on geometry type
    """
    geojson_feat = dict([[k.lower(), v] for (k, v) in geojson_feat.iteritems()])
    assert "type" in geojson_feat, "GeoJSON does not validate.\n\t'type' missing"
    assert "geometry" in geojson_feat, "GeoJSON does not validate.\n\t'geometry' missing"
    assert geojson_feat["type"].lower() == "feature", "GeoJSON does not validate.\n\t'type' is not 'feature'"
    assert "type" in [k.lower() for k in geojson_feat["geometry"].keys()], "GeoJSON does not validate.\n\t'type' is not in 'geometry'"

    if sr is None and "crs" in geojson_feat:
        logger.debug("Looking for feature CRS")

        #to do: probably need some output messages. Just sayin' ;) -- changed by jwx
        try:
            sr = _create_arcpy_sr(geojson_feat["crs"])
        except Exception, e:
            logger.warning(e)
    else:
        assert isinstance(sr, arcpy.SpatialReference), "sr should be an arcpy Spatial Reference"

    with _fc_insert_row(target_fc, sr) as row:
        logger.debug("Adding geometry")
        varshape = read_geometry(geojson_feat["geometry"], sr)
        row.SHAPE = varshape[0]


        logger.debug("Adding attributes")
        for k in geojson_feat:
            if isinstance(geojson_feat[k], dict):
                for attrib, val in geojson_feat[k].iteritems():
                    try:
                        row.setValue(attrib, val)
                    except Exception, e:
                        logger.warning(e)
            else:
                try:
                    row.setValue(k, geojson_feat[k])
                except Exception, e:
                    logger.warning(e)


def read_feature_collection(geojson_feat_collection, target_fc, sr=None):
    """
    Takes a GeoJSON feature collection and iterates through it adding to the
    target feature class.
    """

    geojson_feat_collection = dict([[k.lower(), v] for (k, v) in geojson_feat_collection.iteritems()])
    assert "type" in geojson_feat_collection, "GeoJSON does not validate.\n\t'type' missing"
    assert geojson_feat_collection["type"].lower() == "featurecollection", "GeoJSON does not validate.\n\t'type' is not 'featurecollection'"
    assert "features" in geojson_feat_collection, "GeoJSON does not validate.\n\t'features' missing"

    if sr is None and "crs" in geojson_feat_collection:
        try:
            sr = _create_arcpy_sr(geojson_feat_collection["crs"])
        except Exception, e:
            logger.warning(e)
    else:
        assert isinstance(sr, arcpy.SpatialReference), "sr should be an arcpy Spatial Reference"
    
    logger.debug("Iterating through fc")

    for feat in geojson_feat_collection["features"]:
        read_feature(feat, target_fc, sr)


def dump_geometry(geom):
    ##to do: Implement this!  -- changed by jwx
    """
    Read an arcpy object and return a geojson object
    """
    pass

#def geojsonTofeatureclass(fJson):
#    #http://geojson.org/geojson-spec.html
#    rows = None
#    wkid = -1
#    FC = None;
#    isFeatureCollection = False
#    try:
#        featuregeojson = json.loads(fJson)
#        if(featuregeojson["type"].lower() == "featurecollection"):
#            isFeatureCollection = True
#        #Check for CRS is a geographic coordinate reference system,         
#        if(not featuregeojson["CRS"]):
#            wkid = sr = arcpy.SpatialReference(int('4326'))        
          
#        geom = featuregeojson["geometry"]
#        #http://pro.arcgis.com/en/pro-app/tool-reference/data-management/create-feature-class.htm
#        if(geom.type == "Point"):
#            FC = arcpy.CreateFeatureclass_management("in_memory", "FC", "POINT", spatial_reference=sr) 
#        elif (geom.type == "MultiPolygon" or geom.type == "Polygon"):
            
        

#        #add attributes
#        for (attribute, value) in featuregeojson["properties"].iteritems():
#            arcpy.AddField_management(FC, attribute, "TEXT", field_length=50)
#        #end for  

#        # Create insert cursor for table
#        rows = arcpy.InsertCursor(FC)            
#        #add the json geometry to row
#        row = rows.newRow()
#        row.shape = arcpy.AsShape(geom)

#        #add value to field
#        for (attribute, value) in featuregeojson["properties"].iteritems():
#            row.setValue(attribute, value)
#        #end for 

#        rows.insertRow(row)

#        return FC
#    except:
#        tb = traceback.format_exc()
#        print tb
#    finally:
#        #local cleanup
#        del row
#        del rows  