"""
For plotting WW3 data against observed data. Realtime and archive functionalies.

For realtime plots (and multiprocessing):
    python plots.py -np 8

For specific dates:
    python plots.py -np 8 -s 2020-10-01 -e 2020-10-08

How far out in time plots are created is controlled by variable FHR in the configs.py
file. The long range WW3 model produces output out to 149 hours.
"""
from multiprocessing import Pool
import numpy as np
from scipy import spatial
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, date, timedelta
import argparse
from glob import glob
import os

from configs import M2FT, MS2KT, BUOYS, DATA_DIR, PLOT_DIR, FHR, NUM_DAYS
from configs import ww3_prop, buoy_prop, barb_prop, raw_buoy_prop
from cron_helper import logfile
log = logfile("plots.log")

SCRIPT_PATH = os.path.dirname(__file__) or "."
# --------------------------------------------------------------------------------------
# Function definitions
# --------------------------------------------------------------------------------------
def wind_components(speed, wdir):
    """Calculate the U and V wind vector components from the speed and direction.

    Parameters
    ----------
    speed : float
        The wind speed (magnitude)
    wdir : float
        The wind direction, specified as the direction from which the wind is blowing
        in degrees

    Returns
    -------
    u, v : tuple
        The wind components in the X (East-West) and Y (North-South) directions,
        respectively.
    """
    wdir = np.deg2rad(wdir)
    u = -speed * np.sin(wdir)
    v = -speed * np.cos(wdir)
    return u, v

def parse_time(time_):
    try:
        dt = datetime.strptime(time_, '%Y-%m-%d')
    except:
        return time_
    return dt

def adjust_spines(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 5))
        else:
            spine.set_color('none')
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    else:
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    else:
        ax.xaxis.set_ticks([])

def read_ww3_data(filename):
    """Read Wave Watch III grib2 data"""
    log.info(f"Reading: {filename}")

    data = {}
    ds = xr.open_dataset(filename, engine='cfgrib')
    data = {
        'lons': ds.longitude.values - 360.,
        'lats': ds.latitude.values,
        'wvhgt': ds.swh.values * M2FT,
        'wspd': ds.ws.values * MS2KT,
        'time': pd.to_datetime(ds.valid_time.values),
        'runtime': pd.to_datetime(ds.time.values)
    }
    return data

def read_buoy_data(data_dir, stn_id):
    """Read NDBC Buoy data from text file"""
    try:
        log.info(f"Plotting {stn_id}")
        buoy_data = pd.read_csv(data_dir + '/' + stn_id + '.txt',
                                delim_whitespace=True)[1:]
        buoy_data['datestring'] = buoy_data['#YY'] + buoy_data['MM'] + buoy_data['DD'] \
                                + buoy_data['hh'] + buoy_data['mm']
        wvhgt = pd.to_numeric(buoy_data['WVHT'], errors='coerce') * M2FT
        #buoy_data_derived = pd.read_csv(data_dir + '/' + stn_id + '.dmv',
        #                                delim_whitespace=True)[1:]
        #wspd = pd.to_numeric(buoy_data_derived['WSPD10'], errors='coerce') * MS2KT

        # Correct observed wind speeds to standard 10-m using log-wind profile
        wspd_buoy = pd.to_numeric(buoy_data['WSPD'], errors='coerce') * MS2KT
        wspd_adj = log_wind(wspd_buoy, BUOYS[stn_id][-1])

        wdir = pd.to_numeric(buoy_data['WDIR'], errors='coerce')
        u, v = wind_components(1, wdir)
        dt = pd.to_datetime(buoy_data['datestring'])

        data = {
            'wvhgt': wvhgt,
            'wspd_adj': wspd_adj,
            'wspd': wspd_buoy,
            'u': u,
            'v': v,
            'time': dt
        }
    except (pd.errors.ParserError, pd.errors.EmptyDataError):
        data = None

    return data

def log_wind(buoy_wind, buoy_height):
    """Convert buoy winds to 10-m reference height via log wind profile. This will work
    well in neutral stability environments. Not sure how accurate otherwise. Other
    option is to use NDBCs /derived2 data, but lack of precision seems like a problem
    with those files (units are whole number m/s).

    See this link for further information: https://www.ndbc.noaa.gov/adjust_wind.shtml

    Parameters
    ----------
    buoy_wind : pandas.Dataframe
        Input wind observation
    buoy_height : float
        Height of the buoy above the water. Specified in configs.py

    Returns
    -------
    __ : pandas.Dataframe
        10-m log-wind-corrected wind speed
    """

    return buoy_wind * (10. / buoy_height) ** 0.11

def nearest_idx(points, lon, lat):
    """Search for the nearest grid point using a KDTree

    Parameters
    ----------
    points : list
        List of lists indicating lon/lat pais: [[LON1, LAT1], [LON2, LAT2]]
    lat : np.array
        2-d array of gridded latitudes
    lon : np.arrat
        2-d array of gridded longitudes
    """

    lonlat = np.column_stack((lon.ravel(), lat.ravel()))
    tree = spatial.cKDTree(lonlat)
    dist, idx = tree.query(points, k=1)
    ind = np.column_stack(np.unravel_index(idx, lon.shape))
    return [(j,i) for j,i in ind]

def main(start, end, nproc=None):
    files = []
    start1 = start
    while start1 <= end:
        date_string = datetime.strftime(start1, "%Y-%m-%d")
        files.extend(glob("%s/%s/*.grib2" % (DATA_DIR, date_string)))
        start1 += timedelta(days=1)
    arr = []

    if not nproc:
        for f in files:
            arr.append(read_ww3_data(f))
    else:
        pool = Pool(int(nproc))
        arr = pool.map(read_ww3_data, files)

    colors = plt.cm.Purples_r(np.linspace(0, 1, len(files)))
    for stn_id in BUOYS.keys():
        plt.style.use('%s/style.mplstyle' % (SCRIPT_PATH))
        fig, ax = plt.subplots(2, figsize=(20,8), sharex='col')
        fig.subplots_adjust(hspace=0.15)

        buoy_data = read_buoy_data(DATA_DIR, stn_id)
        points = [BUOYS[stn_id][1], BUOYS[stn_id][0]]

        # WW3 timeseries plots
        for i in range(len(arr)):
            if i == 0: idx = nearest_idx(points, arr[i]['lons'], arr[i]['lats'])
            if i == len(arr)-1:
                ww3_run = 'current'
            else:
                ww3_run = 'past'
                ww3_prop['past']['color'] = colors[i]
            ax[0].plot(arr[i]['time'][0:FHR], arr[i]['wvhgt'][0:FHR,idx[0][0],idx[0][1]],
                       label=arr[i]['runtime'], **ww3_prop[ww3_run])
            ax[1].plot(arr[i]['time'][0:FHR], arr[i]['wspd'][0:FHR,idx[0][0],idx[0][1]],
                       **ww3_prop[ww3_run])

        # Adding in buoy data
        if buoy_data:
            ax[1].quiver(buoy_data['time'], buoy_data['wspd_adj'], buoy_data['u'],
                         buoy_data['v'], **barb_prop)
            ax[1].scatter(buoy_data['time'], buoy_data['wspd_adj'], **buoy_prop)
            #ax[1].scatter(buoy_data['time'], buoy_data['wspd'], **raw_buoy_prop)

            # For stations that don't report wave heights
            if np.nansum(buoy_data['wvhgt']) > 0:
                ax[0].scatter(buoy_data['time'], buoy_data['wvhgt'], **buoy_prop,
                              label=stn_id)
            ax[1].xaxis.set_major_formatter(DateFormatter("%m/%d %H"))

        # Set the axes limits
        ax[0].set_ylim(0, arr[i]['wvhgt'][0:FHR,idx[0][0],idx[0][1]].max()+5)
        ax[1].set_ylim(0, arr[i]['wspd'][0:FHR,idx[0][0],idx[0][1]].max()*2)
        ax[1].set_xlim([start, end + timedelta(hours=FHR)])
        ax[0].set_ylabel('Significant Wave Height (ft)', fontsize=12)
        ax[1].set_ylabel('Wind Speed (kts) (10-m adjusted)', fontsize=12)
        ax[1].set_xlabel('Valid Date', fontsize=12)

        # Adding vertical time reference
        ymin, ymax = ax[0].get_ylim()
        ax[0].vlines(NOW, ymin, ymax, linestyles='dashed', colors='#ffffff')
        ax[0].text(NOW+timedelta(hours=1), ymax, NOW.strftime('%c'), color='red')
        ymin, ymax = ax[1].get_ylim()
        ax[1].vlines(NOW, ymin, ymax , linestyles='dashed', colors='#ffffff')

        # ------------------------------------------------------------------------------
        # Adjusting x- and y-axes. Could be moved to a function.
        # ------------------------------------------------------------------------------
        ax[0].tick_params('both', length=7.5, width=2, which='major')
        ax[0].spines['top'].set_color('none')
        ax[0].spines['right'].set_color('none')
        ax[0].spines['bottom'].set_linewidth(2)
        ax[0].spines['left'].set_linewidth(2)
        adjust_spines(ax[0], ['left', 'bottom'])

        ax[1].tick_params('both', length=7.5, width=2, which='major')
        ax[1].spines['top'].set_color('none')
        ax[1].spines['right'].set_color('none')
        ax[1].spines['bottom'].set_linewidth(2)
        ax[1].spines['left'].set_linewidth(2)
        adjust_spines(ax[1], ['left', 'bottom'])

        plt.savefig("%s/%s.png" % (PLOT_DIR, stn_id), bbox_inches='tight', dpi=250)
        plt.close()

    t2 = datetime.now()
    delta = t2 - t1
    print("===========================================================================")
    log.info(f"Completed Plotting in {delta.total_seconds()} seconds")
    print("===========================================================================")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start', dest="start", help="YYYY-MM-DD")
    ap.add_argument('-e', '--end', dest="end", help="YYYY-MM-DD")
    ap.add_argument('-np', '--nproc', dest='nproc',
                    help="If using mproc for data read, specify number of cores")
    args = ap.parse_args()

    t1 = datetime.now()
    log.info("Begin WW3 Plotting routines...")
    NOW = datetime.now()
    if args.start is not None:
        start = parse_time(args.start)
    else:
        start = parse_time(NOW - timedelta(days=NUM_DAYS))

    if args.end is not None:
        end = parse_time(args.end)
    else:
        end = parse_time(NOW)

    main(start, end, nproc=args.nproc)
