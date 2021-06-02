# ac_python_logger #
A python logger for [ESPHome AUX air conditioner custom component](https://github.com/GrKoR/esphome_aux_ac_component).

Use this script to log data from the [ESPHome AUX air conditioner custom component](https://github.com/GrKoR/esphome_aux_ac_component).
All bytes received by component are saved to CSV (comma separated) text file. You can analyze it in case of component malfunction.

Also csv logs can be sent to component author as a part of issue report.

# How to install #

## Step 1: python installation ##
You need a python installed. See [Python beginners guide](https://wiki.python.org/moin/BeginnersGuide) for details.

## Step 2: modules ##
Next you need this modules:
1. [aioesphomeapi](https://github.com/esphome/aioesphomeapi)
2. [asyncio](https://docs.python.org/3/library/asyncio.html)

Installation of this modules is simple and [described in official guide](https://docs.python.org/3/installing/index.html). You just need commands:
```
python -m pip install aioesphomeapi
python -m pip install asyncio
```

## Step 3: logger ##
Download [logger script](https://raw.githubusercontent.com/GrKoR/ac_python_logger/main/ac_logger.py) to your local folder.

Create `secrets.py` file in the same folder. This file must contain sensitive data like this:
```python
AC_IP = "10.10.0.100"
AC_PASS = "YourESPHomeAPIPassword"
```

# How to use it #

## Run the script ##
The following command will run script:
```
py ac_logger.py
```

Script will work till you stop it by CTRL+C.
During the script execution you will see logger messages on the screen. Something like this:
```
2021-06-02 22:22:22,0000123456,[<=],BB,00,01,00,00,00,00,00,43,FF
```

When you start script it creates new csv-file for writing data. File name format is `YYYY-MM-DD hh-mm-ss AC-DATA.csv`. You can change filename in the script source as you wish.

## The results ##
Every time when logger receives data it will save it to CSV file. This file is located in the current folder.
You may open this file without script termination if your csv-viewer isn't locking csv-file. For example Notepad++.

Open file with Excell or LibreOffice for analyze. But before this you need to terminate script cause spreadsheet processor may lock the csv-file.