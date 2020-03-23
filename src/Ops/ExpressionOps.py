#------------------------------------------------------------------------------
#----- ExpressionOps.py ------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2017 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  A simple log tracking application for StreamStats.
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:   05 NOV 2017 jkn - Created
#               04 APR 2018 jkn - Modified method types
#
#------------------------------------------------------------------------------

def Evaluate(procedure, funcArgs, weightArgs = None):
    method = procedure.lower()
    if (len(funcArgs)!= _getFunctionArgNumber(method)): raise Exception("invalid number of arguments passed")
    if (len(weightArgs)!= None and len(funcArgs) != len(weightArgs)): raise Exception("funcArgs must match WeightedArgs")

    if method == 'sum':
        # Do the Sum
        result = sum(funcArgs)
    elif method == 'weightedaverage':
        # Do the WeightedAverage
        weightSum = sum(weightArgs);
        if (weightSum <= 0): raise Exception("Weight sum < 0")
        weightval = [val * wt/weightSum for val, wt in zip(funcArgs, weightArgs)]
        result = sum(weightval)

    elif method == 'weighteddifference':

        try:
            # Do the WeightedAverage
            for i in [i for i, val in enumerate(funcArgs) if val is None]:
                del funcArgs[i]
                del weightArgs[i]

            if len(funcArgs) < 1:
                result = 0
            elif len(funcArgs) == 1:
                result = funcArgs[0]
            else:
                weightTot = weightArgs[0] - sum(weightArgs[1:])
                weightval = [val * wt / weightTot for val, wt in zip(funcArgs, weightArgs)]

                result = weightval[0] - sum(weightval[1:])
        except:
            result = 0


    elif method == 'difference':
        # Do The Subract
        result = funcArgs[0] - sum(funcArgs[1:])

    elif method =='none':
        result = funcArgs[1]

    else:
        raise Exception("Procedure not yet implemented: "+ procedure)# + procedureEnum)
    
    return result

def _getFunctionArgNumber(procedure):
    method = procedure.lower()
    if method == "sum": return 2
    elif method == "weightedaverage": return 2
    elif method == "weighteddifference": return 2
    elif method == "difference": return 2
    elif method =="none": return 2

