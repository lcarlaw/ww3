# --------------------------------------------------------------------------------------
#
# CONFIGURATION FILE
# .condarc:
#    channels:
#       - conda-forge
#       - defaults
# conda create --name ww3 python=3.7
# conda activate ww3
# conda install xarray pandas cfgrib scipy matplotlib
# --------------------------------------------------------------------------------------
DATA_DIR = "/Users/leecarlaw/scripts/ww3/data"
PLOT_DIR = "/Users/leecarlaw/scripts/ww3/images"

# Buoy metadata. Information within the buoys dictionary is in the form:
#   'BUOY ID': [LAT, LON, ANEMOMETER HEIGHT]
BUOYS = {
    # LOT
    #'45174': [42.135, -87.655, 3.],
    #'45170': [41.755, -86.968, 2.5],
    #'45168': [42.397, -86.331, 3.],
    #'45198': [41.892, -87.563, 1.5],
    'CHII2': [41.856, -87.609, 26.],
    'MCYI3': [41.729, -86.912, 21.3],
    #'WHRI2': [42.361, -87.813, 9],

    # MKX
    #'45186': [42.368, -87.779, 1.5],
    #'45187': [42.491, -87.779, 1.5],
    'KNSW3': [42.589, -87.809, 20],
    'MLWW3': [43.005, -87.884, 7.3],
    #'45013': [43.100, -87.850, 2],
    #'45007': [42.674, -87.026, 3.6],
    #'45002': [45.344, -86.411, 3.8],
    '45214': [42.674, -87.026, 1.0], 

    # IWX/GRR
    #'45029': [42.900, -86.272, 3.],
    #'45026': [41.982, -86.619, 3.],
    #'SJOM4': [42.098, -86.494, 10], # At the lake?
    #'BHRI3': [41.646, -87.147, 10],
    #'SVNM4': [42.401, -86.288, 16.8],
    #'HLNM4': [42.773, -86.213, 10.4],
    #'45161': [43.185, -86.355, 2.3],
    #'MKGM4': [43.227, -86.339, 24.4],
    #'LDTM4': [43.947, -86.441, 7.7],
    #'45024': [43.955, -86.554, 2.95],
    #'BSBM4': [44.055, -86.514, 10.],
    #'MEEM4': [44.251, -86.342, 12.2]
}

# Variables for automated WW3 downloads.
# SLEEP_TIME : number of seconds to sleep between download calls for ww3 data
# TIME_LIMIT : number of hours to try and download data before exiting
SLEEP_TIME = 120
TIME_LIMIT = 2

# ======================================================================================
# Plotting configurations.
# Additional matplotlib styling information can be specified in the style.mplstyle file.
# ======================================================================================
ww3_prop = {
    'current': {
        'color': 'cyan',
        'linewidth': 4
    },
    'past': {
        'linewidth': 2
    }
}
buoy_prop = {'marker': 'o', 's': 5, 'c': 'r', 'linewidths': 2, 'zorder': 99}
raw_buoy_prop = {'marker': 's', 's': 3, 'c': 'b', 'linewidths': 1, 'zorder': 4}
barb_prop = {'color': '#84fa75', 'width': 0.0008, 'headwidth': 5, 'scale': 65,
             'headlength': 8, 'headaxislength': 6, 'zorder': 3}

# WW3 forecast hours to plot (max=149)
FHR = 84

# Number of days of WW3 in the past to plot
NUM_DAYS = 5

# ======================================================================================
# Likely no need for editing below this line
# ======================================================================================
# Data URLs
BUOY_URL = "https://www.ndbc.noaa.gov/data/realtime2/"
REALTIME_URL = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/glwu/prod/glwu."

# Data variables we want from the wave model
GRIB_VARS = ":(WIND|WDIR|HTSGW):"

# NDBC seems to hide this directory, which contains 10- and 20-m-corrected winds  using
# an interative bulk momentum parameterization defined by [1]_. These values don't seem
# super useful, however, since they're all just int8s? Seems like a big loss of
# precision with units in m/s.
#
# [1]_ .. Liu, W. T., K. B. Katsaros, and J. A. Businger, 1979: Bulk Parameterizations
#          of Air-Sea Exchanges of Heat and Water Vapor Including Molecular Constraints
#          at the Interface, Journal of Atmospheric Science, Vol. 36, 1722-1735.
# BUOY_URL2 = "https://www.ndbc.noaa.gov/data/derived2/"

# Standard atmospheric conversions
M2FT = 3.28084
MS2KT = 1.94384
