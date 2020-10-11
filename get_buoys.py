from subprocess import Popen, PIPE
try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which
from configs import BUOYS, BUOY_URL, DATA_DIR
from cron_helper import timestamp

# Logic to find wget or curl on the system
WGET = which('wget')
if not WGET:
    CURL = which('curl')
if not WGET and not CURL:
    raise ValueError("Neither wget nor curl found on the system. Exiting")

for buoy in BUOYS.keys():
    url = "%s/%s.txt" % (BUOY_URL, buoy)
    if WGET:
        p = Popen([WGET, '-O', '%s/%s.txt' % (DATA_DIR, buoy), url], stderr=PIPE)
    elif CURL:
        p = Popen([CURL, '-o','%s/%s.txt' % (DATA_DIR, buoy), url], stderr=PIPE)
    p.wait()
    timestamp("INFO", url)
