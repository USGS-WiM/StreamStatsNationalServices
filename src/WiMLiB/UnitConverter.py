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
#   mod work:   Pull from HydroOps - Tutorial with Jeremy (DONE)
#               AnthOps (DONE)
#               GeogOps (N/A)
#               PhysOps (N/A)
#
# add. notes:  Initially developed from code by Jeremy
#
#------------------------------------------------------------------------------

#Library of conversions
#Length
#   Meters to...
CF_M2FT = 3.28083
CF_M2IN = 39.37007874                       # 1 meter = 39.37007874 inch
CF_M2MI = 0.0006213712                      # 1 meter = 0.0006213712 miles
CF_M2MM = 1000                              # 1 meter = 1000 millimeter
CF_SQKM2SQM = 1000000                       # 1 square kilometer = 1 000 000 square meter

#   Centimers to...
CF_CM2FT = 0.0328083                        # 1 centimeter = 0.0328083 foot
cf_CM2IN = 0.3937007874                     # 1 centimeter = 0.3937007874 inch
CF_CM2MM = 10                               # 1 centimeter = 10 millimeter
CF_CM2M = 0.01                              # 1 centimeter = 0.01 meters

#   Feet to...
CF_FT2IN = 12.0                             # 1 foot to inches @ 12 in/ft
CF_FT2CM = 30.48                            # 1 foot = 30.48 centimeters 
CF_FT2M = 0.3048                            # 1 foot = 0.3048 meters
CF_FT2MM = 304.8                            # 1 feet = 304.8 millimeter
CF_IN2MM = 25.4                             # 1 inch = 25.4 millimeter
CF_IN2M = 0.0254                            # 1 inch = 0.0254 meter

#Area
#   Acres to...
CF_ACR2SQKILOMETER = 0.00404685642          # 1 acres = 0.00404685642 square kilometers

#   Square Kilometers to...
CF_SQKILOMETER2SQMM = 1000000000000         # 1 square kilometer = 1,000,000,000,000 square millimeters
CF_SQKILOMETER2SQFOOT = 10763910.4          # 1 square kilometer = 10 763 910.4 square feet

#   Square Meters to...
CFR_SQMETER2SQMI = 0.00000259000259000259   # 1 / (1000000 * 0.3861) reciprocal multiplier avoids division

#   Square Feet to...
CF_SQFOOT2SQKILOMETER = 0.00000009290304    # 1 square foot = 9.290304 × 10-8 square kilometers
CF_SQMETERS2SQKILOMETER = 0.000001          # 1 square meter = 1.0 × 10-6 square kilometers

#Volume
#   Acre-feet to...
CF_ACFT2CUBICM = 1233.0                     # 1 acre/ft to cubic meters
    
#   Cubic Feet to...
CF_CUBICFT2CUBICM = 0.0283168466            # 1 cubic foot = 0.0283168466 cubic meters
    
#   Cubic Meters to...
CF_CUBICM2CUBICFT = 35.31467                # cubic meters to cubic feet

class UnitConverter(WiMLib):
    def 