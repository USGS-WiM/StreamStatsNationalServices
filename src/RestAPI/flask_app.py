'''
Created on Apr 10, 2017

@author: gpetrochenkov
'''
from flask import Flask, jsonify, request, Response
from dicttoxml import dicttoxml
from RestAPI.utilities import check_exists, validate_format
from RestAPI.service_workers import get_comma_sep_values, basin_chars
import os
from RestAPI.service_workers import delineate

app = Flask(__name__)

#--------------------------REST ENDPOINTS--------------------------

@app.route('/streamstatsservices/parameters.<string:format_type>', 
           methods=['POST'])
def basinCharacteristics(format_type):
    '''Endpoint for basin characteristics availability and statistics'''
    args_dict = {}
    
    #validates output format
    args_dict['format'] = validate_format(format_type, ['xml','json'])
    
    #check for required parameters
    #args_dict['rcode'] = check_exists('rcode', request.args)
  
    #necessary for computing basin characteristics
    if 'workspaceID' in request.args and request.args['workspaceID'] != '':
        args_dict['workspaceID'] = str(request.args.get('workspaceID'))
        
    #optional arguments
    if 'group' in request.args:
        args_dict['group'] = str(request.args.get('group'))
    if 'includeparameters' in request.args:
        args_dict['includeParameters'] = get_comma_sep_values( 
                            str(request.args.get('includeparameters')))
    
    data = basin_chars(data=args_dict)
    
    if format_type == 'xml':
        
        def default_xml(x):
            if x == 'parameters':
                return 'parameter'
            if x == 'messages':
                return 'message'
        
        return Response(dicttoxml({'parameters': data, 'messages': ['Count %d' % len(data)]}, item_func=default_xml), mimetype='text/xml')
    else:
        return jsonify(**{'parameters': data, 'messages': ['Count %d' % len(data)]})
    
    
@app.route('/streamstatsservices/watershed.<string:format_type>', 
           methods=['POST'])
def watershed(format_type):
    '''Endpoint for watershed queries'''
    
    args_dict = {}
   
    #validates output format
    args_dict['format'] = validate_format(format_type,
                                          ['xml','json', 'geojson'])
    
    #Check if the required parameters entered
    args_dict['crs'] = str(check_exists('crs', request.args))
   
    if (('xlocation' not in request.args or 'ylocation' not in request.args) \
        and 'workspaceID' not in request.args \
        and 'comid' not in request.args):
        raise Exception('Need either both the xlocation and ylocation or \
                        the workspace ID')
        
    #necessary for pour point watershed query
    if 'xlocation' in request.args and 'ylocation' in request.args:
        try:
            args_dict['xlocation'] =  float(request.args.get('xlocation'))
            args_dict['ylocation'] = float(request.args.get('ylocation'))
        except:
            raise Exception('xlocation and/or ylocation not valid numbers')
    
    #necessary for workspace ID watersehd query
    if 'workspaceID' in request.args:
        args_dict['workspaceID'] = str(request.args.get('workspaceID'))
     
    #necessary for pout point watershed query if x/y points not provided   
    if 'comID' in request.args:
        args_dict['comID'] = str(request.args.get('comID'))
    
    #optional arguments
    if 'includeparameters' in request.args:
        args_dict['includeParameters'] = get_comma_sep_values( 
                            str(request.args.get('includeparameters')))
        
    if 'includefeatures' in request.args:    
        args_dict['includeFeatures'] = get_comma_sep_values(
                            str(request.args.get('includefeatures')))
        
    if 'simplify' in request.args:
        args_dict['simplify'] = str(request.args.get('simplify')) == 'true'
    
    data = delineate(data = args_dict)
    
    if args_dict['format'] == 'xml':
        
        def default_xml(x):
            if x == 'features':
                return 'feature'
            if x == 'coordinates':
                return 'ArrayOfDouble'
            if x == 'ArrayOfDouble':
                return 'double'
            
        return Response(dicttoxml({'watershed': data}, item_func=default_xml), mimetype='text/xml')
    else:
        return jsonify(**data)
       
       
@app.route('/streamstatsservices/download', methods=["POST"])
def download():
    
    args_dict = {}
    
    #check for required parameters
    check_exists('workspaceID', request.args)
    
    #necessary for download query
    args_dict['workspaceID'] = str(request.args.get('workspaceID'))
    
    #optional arguments
    #ASK about valid input: so far only a Zipped GDB or a SHAPE format
    if 'format' in request.args:
        args_dict['format'] = validate_format(str(request.args.get('format')), 
                                              ['', 'SHAPE'])
        
     
#     do_work(data = args_dict)
    
    data = {"message": "success"}
    return jsonify(**data)


@app.route('/streamstatsservices/flowstatistics.<string:format_type>',
           methods=['POST'])
def flow_statistics(format_type):
    
    args_dict = {}
   
    #validates output format
    args_dict['format'] = validate_format(format_type, ['json'])
    
    #check for required parameters
    args_dict['rcode'] = str(check_exists('rcode', request.args))
    
    #necessary for computing flow characteristics
    if 'workspaceID' in request.args:
        args_dict['workspaceID'] = str(request.args.get('workspaceID'))
        
    #optional arguments
    if 'includeflowTypes' in request.args:
        args_dict['includeFlowTypes'] = get_comma_sep_values(
                            str(request.args.get('includeflowtypes')))
        
#     do_work(data = args_dict)
    data = {"message": "success"}
    return jsonify(**data)

 
@app.route('/streamstatsservices/features.<string:format_type>',
           methods=['POST'])
def features(format_type):
    
    args_dict = {}
   
    #validates output format
    args_dict['format'] = validate_format(format_type, \
                                          ['xml','json', 'geojson'])
    
    #check for required parameters
    args_dict['workspaceID'] = str(check_exists('workspaceID', request.args))
   
    #necessary to return features
    if 'includefeatures' in request.args:    
        args_dict['includeFeatures'] = get_comma_sep_values(
                            str(request.args.get('includefeatures')))
    else:
        if format_type == 'geojson': raise Exception('Not valid output format'\
                                                    'for availability')
        
    #optional arguments
    if 'simplify' in request.args:
        args_dict['simplify'] = str(request.args.get('simplify')) == 'true'
    if 'crs' in request.args:
        args_dict['crs'] = str(request.args.get('crs'))
                
#     do_work(data = args_dict)
    data = {"message": "success"}
    return jsonify(**data)   
    
    
if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run()
