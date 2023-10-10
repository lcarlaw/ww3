"""
Run at 7:30 and 19:30 UTC to grab full WW3 runs
"""
import time
from datetime import datetime
import os, sys, errno
from subprocess import Popen, PIPE
import subprocess
try:
    from urllib.request import urlopen, URLError        # Python 3
except ImportError:
    from urllib2 import urlopen, URLError               # Python 2
import argparse
from cron_helper import logfile
log = logfile(f"ww3.log")
from configs import GRIB_VARS, DATA_DIR, REALTIME_URL, SLEEP_TIME, TIME_LIMIT

SCRIPT_PATH = os.path.dirname(__file__) or "."
def timeout_check():
    """Determine how long this process has been running. Kill it if over TIME_LIMIT
    """
    NOW = time.time()
    if NOW - THEN > TIME_LIMIT * 3600:
        log.error("Exceeded time limit")
        sys.exit(1)

def is_url_alive(url):
    """Test for file existence on the NOMADS server by looking for the corresponding
    .idx file

    Parameters
    ----------
    url : str
        URL to test for existence on the NOMADS server

    Returns
    -------
     __ : bool
    """

    try:
        urlopen(url, timeout=10)
        return True
    except URLError:
        return False
    except socket.timeout:
        return False
    except socket.error:
        return False

def get_filesize(fname):
    """Test filesize on the local system. If the file DNE, return a filsize of 0 bytes.

    Parameters
    ----------
    fname : str
        Location on the local file system to grab filesize for

    Returns
    -------
    fsize : int
        Filsize (bytes)
    """

    try:
        fsize = os.stat(fname).st_size
    except:
        fsize = 0
    return fsize

def get_ww3(run_time):
    """Download realtime WW3 data from the NCEP NOMADS server. This function uses
    Wesley Ebisuzaki's get_inv.pl and get_grib.pl scripts to allow downloading of a
    small subset of the full grib2 data files. Saves a ton of space and time!
    Further information can be found at [1]_ below.

    [1]_: Ebisuzaki, W.: Fast Downloading of GRIB Files: Partial http transfers.
              https://www.cpc.ncep.noaa.gov/products/wesley/fast_downloading_grib.html

    Parameters
    ----------
    run_time : string
        Time of the model run to be downloaded. For is: YYYY-MM-DD/HH

    Returns
    -------
    Individual .grib2 files downloaded to the local system.
    """

    dt = datetime.strptime(run_time, '%Y-%m-%d/%H')
    data_path = "%s/%s" % (DATA_DIR, dt.strftime('%Y-%m-%d'))

    # Not too pretty, but watch for a potential RACE conditions on multiple crons?
    try:
        os.makedirs(data_path)
    except OSError as e:
        if e.errno != errno.EEXIST: raise

    date_str = dt.strftime('%Y%m%d%H')
    fname = 'glwu.grlc_2p5km.t%sz.grib2' % (date_str[-2:])
    url = '%s%s/%s' % (REALTIME_URL, date_str[0:8], fname)
    full_name = data_path + '/' + fname

    # Shell argument string to invoke the get_grib.pl script.
    arg = '%s/etc/get_inv.pl %s.idx | egrep "%s" | %s/etc/get_grib.pl %s %s' \
           % (SCRIPT_PATH, url, GRIB_VARS, SCRIPT_PATH, url, full_name)

    # Test for file existence.
    num_attempts = 1
    file_exists = False
    while not file_exists and num_attempts < 90 and not os.path.exists(full_name):
        file_exists = is_url_alive(url)

        if file_exists:
            # As long as we trust the input argument here. Don't extend this to take a
            # command-line argument, however.
            subprocess.call(arg, shell=True)
            log.info("Downloading %s" % (full_name))
            break
        else:
            log.info("Can't find %s. Sleeping." % (url))

        num_attempts += 1
        time.sleep(SLEEP_TIME)
        timeout_check()

    # Test for file size on the local system.
    num_attempts = 1
    file_size = get_filesize(full_name)
    while file_size < 10 and num_attempts < 10:
        file_size = get_filesize(full_name)
        log.warning("File not of expected size. Re-downloading")
        subprocess.call(arg, shell=True)
        num_attempts += 1
        time.sleep(SLEEP_TIME)
        timeout_check()

ap = argparse.ArgumentParser()
ap.add_argument('-t', '--time-str', dest="time_str", help="YYYY-MM-DD/HH")
args = ap.parse_args()

if not args.time_str:
    # No arguments passed. Cycle time will be the current hour.
    NOW = datetime.utcnow()
    time_str = NOW.strftime('%Y-%m-%d/%H')
else:
    # User-specified cycle time
    time_str = args.time_str

THEN = time.time()
log.info("Starting WW3 Download for %s" % (time_str))
get_ww3(time_str)
log.info("Download Complete")
