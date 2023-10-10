from datetime import datetime
import logging
import os
SCRIPT_PATH = os.path.dirname(__file__) or "."

def timestamp(str1, str2):
    """Print out some simple date and time information for log files
    """
    print("%s  %s : %s" % (str1, datetime.strftime(datetime.now(), "%c"), str2))

def logfile(logname):
    logging.basicConfig(filename="%s/%s" % (f"{SCRIPT_PATH}/logs", logname),
                        format='%(levelname)s %(asctime)s :: %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S")
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    return log
