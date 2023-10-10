import schedule
import time
import os
SCRIPT_PATH = os.path.dirname(__file__) or "."
import subprocess
from cron_helper import logfile

PYTHON = "/Users/leecarlaw/anaconda3/envs/ww3/bin/python"

def execute(arg):
    process = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,
              stderr=subprocess.PIPE)
    process.communicate()
    return process

def make_plots():
    arg = f"{PYTHON} {SCRIPT_PATH}/get_buoys.py"
    log.info(f"Executing {arg}...")
    p = execute(arg)

    arg = f"{PYTHON} {SCRIPT_PATH}/plots.py -np 8"
    log.info(f"Executing {arg}...")
    p = execute(arg)

    arg = f"{PYTHON} {SCRIPT_PATH}/uploader.py {SCRIPT_PATH}/images/*.png"
    log.info(f"Executing {arg}...")
    p = execute(arg)

def download_ww3_data():
    arg = f"{PYTHON} {SCRIPT_PATH}/get_ww3.py"
    log.info(f"Downloading WWIII data...")
    p = execute(arg)

log = logfile(f"cron.log")
task = schedule.Scheduler()
task.every().hour.at(":00").do(make_plots)
task.every().hour.at(":30").do(make_plots)
task.every().day.at("07:35").do(download_ww3_data)
task.every().day.at("19:35").do(download_ww3_data)

while True:
    task.run_pending()
    time.sleep(1)
