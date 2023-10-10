# ww3
The code in this repo downloads buoy data from the National Data Buoy Center ([NDBC](https://www.ndbc.noaa.gov/)) and Great Lakes [Wave Watch III](https://polar.ncep.noaa.gov/waves/wavewatch/) numerical model to produce real time plots of forecast and observed Significant Wave Heights and 10-m winds. Presently, graphs are uploaded to a [Google Drive Folder](https://drive.google.com/drive/folders/1PdbtaISRJxTEyEpOzfvP-BmgfyjUuetX?usp=sharing) every hour. In the future, I may migrate everything into a Dash Application to allow for more user interaction with map-based data, but with the buoys likely to be pulled soon, this project will wait until later this winter or next spring.

The goals of this project are multifold. The first is the provide operational meteorologists a means to easily compare observed wave and wind information to the latest forecast to enhance situational awareness. The second—more specific goal—is to develop the skeleton code and archive for a more robust verification of the forecast wave action in the southern Lake Michigan nearshore waters, specifically in the vicinity of the Wilmette, Illinois and Michigan City, Indiana buoys.

![](https://raw.githubusercontent.com/lcarlaw/ww3/main/images/45174.png)
<p align="center">
  <em>Example output plot. Significant wave heights (top; ft) and Wind Speeds (bottom; kts). Observations are displayed as red dots. The latest WW III run is displayed as a thick cyan line, with older runs (back to 5 days) progressing from white to dark purple.
  </em>
</p>

## Basic Setup Notes

This code was developed using Anaconda and Python 3.7. While no guarantees can be made, the scripts in this repo should be backwards compatible with Python 2.xx.

### Anaconda Environment and Packages

You may need to add conda-forge to your conda configuration file:

```
conda config --add channels conda-forge
```

The Anaconda environment set up looks like this:

```
conda create --name ww3 python=3.7
conda activate ww3
conda install xarray pandas cfgrib scipy matplotlib curl schedule
[optional] conda install pydrive (for automated Google Drive uploads)
```

## Usage

The expected code structure is as follows. Ensure you have write permissions to each of the listed subdirectories.

```
ww3/
configs.py
get_buoys.py
get_ww3.py
plots.py
style.mplstyle
uploader.py
cron_helper.py
|————etc/
       |————get_grib.pl
       |————get_inv.pl
|————images/
|————logs/
|————data/
```

### [1] Configuration file: configs.py

Variables ```DATA_DIR``` and ```PLOT_DIR``` must be edited to reflect the desired location on the local file system. ```BUOYS``` is a Python dictionary which can be edited to add (or remove) buoys or marine platforms to the plotting cycle. **Note that some observation sites may appear to be 'on land' to the interpolation routine, and respective latitude/longitude pairs may need to be altered as a result.** Additional user-configurable variables are documented throughout this file.

### [2] NDBC-based downloads: get_buoys.py

User edits shouldn't be necessary for this script, as it will search the file system for an executable ```CURL``` or ```WGET``` binary. If neither can be found, the script will fail and exit. This script takes no arguments.

```
python get_buoys.py
```

Text files will be downloaded and stored in the ```/data``` directory.

### [3] Wave Watch III downloads: get_ww3.py

This script will fetch WW3 GRIB2 files from the [NCEP NOMADS server] (https://nomads.ncep.noaa.gov/pub/data/nccf/com/wave/prod/). The full "long term" (to 149 hours) WW3 data is generally available around 19:25 and 7:25 UTC.

One command-line argument is required:

```
python get_ww3.py -t [CYCLE_TIME]
```

 - ```CYCLE_TIME``` is the requested WW3 cycle in the form ```YYYY-mm-dd/HH```

#### Requirements

The code here utilizes the ```get_grib.pl``` and ```get_inv.pl``` scripts in the ```/etc``` folder to download a subset of the GRIB2 files which are natively nearly ```1 GB``` in size. The only variables we need are Significant Wave Height, Wind Speed, and Wind Direction, which are specified in the ```GRIB_VARS``` variable in ```config.py```. The two perl scripts require ```CURL``` to be in the local ```$PATH``` variable.

### [4] Plotting routines: plots.py

This script can be run in either a multiprocessing or serial mode. In multiprocessing mode: ```python plots.py -np 8```, several processes will be initialized, each one responsible for reading an individual WW3 model cycle. This is recommended given the file sizes which are each about ```25-30 MB```. The ```-np``` flag can be left off for a serial run.

Plots will be created for each of the dictionary entries specified in the ```BUOYS``` variable in ```configs.py``` and saved into the ```/images``` directory.

#### Interpolation and Wind-adjustment routines

Function ```nearest_idx``` linearly interpolates the gridded WW3 data to each buoy point using ```scipy.sptial.cDKTree``` which is a subset of ```KDTree``` but implemented in C++ and wrapped in Cython for efficiency. The interpolation may fail if grid points around the buoy location are identified as 'land-based'.

Function ```log_wind``` applies a simple logarithmic function to adjust marine-platform-observed winds to a standard 10-m reference height. The current implementation of this routine is naive to the low-level static stability profile, and likely will not work appropriately for anything other than near-neutrally-stable atmospheric conditions. Improvements to this function may be made at a later time, especially to provide better wind speed reductions from the 20-30+ m GLERL/C-MAN-based anemometers.

### [5] [Optional] Upload to Google Drive Folder: uploader.py

First, you must following the steps on this page ```https://pythonhosted.org/PyDrive/quickstart.html``` to enable OAuth verification and to generate your personal ```client_secrets.json``` file (follow steps 1 - 5).

Once this is completed, run:

```
python init_authorization.py
```

This will authenticate your tokens and store the pertinent data within ```credentials.txt``` and you should be ready to go.

To use the automated uploader script, set up a Google Drive folder and update the ```folder``` variable with the appropriate ID.  Usage is:

```
python uploader images/*.png logs/*.log
```

### [6] Script automation:

```
# WW3
25 * * * * $PYTHON ${WW3_DIR}/get_buoys.py > ${WW3_DIR}/logs/buoys.log 2>&1
25 7,19 * * * $PYTHON ${WW3_DIR}/get_ww3.py > ${WW3_DIR}/logs/ww3.log 2>&1
27 * * * * $PYTHON ${WW3_DIR}/plots.py -np 8 > ${WW3_DIR}/logs/plots.log 2>&1
29 * * * * $PYTHON ${WW3_DIR}/uploader.py  ${WW3_DIR}/images/*.png ${WW3_DIR}/logs/*.log
```
