#------------------------------------------------------------------------------
#----- UnitConverter.py -------------------------------------------------------
#------------------------------------------------------------------------------
#
# copyright:   2017 WiM - USGS
#
#    authors:  John Wall - Ph.D. Student NC State University
#
#    purpose:  This code performs various conversion calculations for StreamStats
#
#      dates:  28 FEB 2017 - Created
#
# add. notes:  Initially developed from code by Jeremy K. Newson
#
#------------------------------------------------------------------------------

#Length Dictionary
linear = {
    'KMtoM': 1000, 'KMtoCM': 100000, 'KMtoMM': 1000000, 'KMtoMI': 0.621371, 'KMtoFT': 3280.84, 'KMtoIN': 39370.1,
    'MtoKM': 0.001, 'MtoCM': 100, 'MtoMM': 1000, 'MtoMI': 0.0006213712, 'MtoFT': 0.3048, 'MtoIN': 39.37007874,
    'CMtoKM': 0.00001, 'CMtoM': 0.1, 'CMtoMM': 10, 'CMtoMI': 0.0000621371, 'CMtoFT': 0.0328084, 'CMtoIN': 0.393701,
    'MMtoKM': 0.000006, 'MMtoM': 0.001, 'MMtoCM': 0.1, 'MMtoMI': 0.00000062137, 'MMtoFT': 0.00328084, 'MMtoIN': 0.0393701,
    'MItoKM': 1.60934, 'MItoM': 1609.34, 'MItoCM': 160934, 'MItoMM': 1609000, 'MItoFT': 5280, 'MItoIN': 63360,
    'FTtoKM': 0.0003048, 'FTtoM': 3.28083, 'FTtoCM': 30.48, 'FTtoMM': 304.8, 'FTtoMI': 0.000189394, 'FTtoIN': 12,
    'INtoKM': 0.0000245, 'INtoM': 0.0254, 'INtoCM': 2.54, 'INtoMM': 25.4, 'INtoMI': 0.0000157828, 'INtoFT': 0.0833333,
}

#Rudimentary module
def Convert(value, inUnits, outUnits, dimentionality):
    if inUnits == outUnits:
        print "No Conversion Needed"
    else:
        print "In units do not match output units. A conversion will be made."
        #Create a string for the conversion look up rule
        conversionRule = '%s to %s' % (inUnits, outUnits) #Build conversion rule
        conversionRule.replace(" ", "")                   #Convert to look-up key

        #Choose dictionary based on being a line, area, or volume
        if dimentionality == 1:
            outValue = value * linear[conversionRule]
            return outValue
        elif dimentionality == 2:
            outValue = value * area[conversionRule] #Needs to be added later
            return outValue
        elif dimentionality == 3:
            outValue = value * volume[conversionRule] #Needs to be added later
            return outValue
        else:
            print "Dimentionality was undefined."