# ac_python_logger #
A python logger for [ESPHome AUX air conditioner custom component](https://github.com/GrKoR/esphome_aux_ac_component).
New version of the script allow you collect log data from multiple AUX devices in your local network. It is very useful for multisplit systems or in case of monitoring several independent HVAC.

Use this script to log data from the [ESPHome AUX air conditioner custom component](https://github.com/GrKoR/esphome_aux_ac_component).
All bytes received by component are saved to CSV (comma separated) text file. You can analyze it in case of component malfunction.
This script can also write temperature data to the log (-d command line param of the script). 

Also csv logs can be sent to [ac_aux component](https://github.com/GrKoR/esphome_aux_ac_component) author as a part of issue report.

# How to install #

## Step 1: python installation ##
You need a `python 3.7` or newer installed. See [Python beginners guide](https://wiki.python.org/moin/BeginnersGuide) for details.

If you already have the python check it version with this command:
```
python --version
```

## Step 2: modules ##
Next you need this modules:
1. [aioesphomeapi](https://github.com/esphome/aioesphomeapi)
2. [asyncio](https://docs.python.org/3/library/asyncio.html)

Installation of this modules is simple and [described in official guide](https://docs.python.org/3/installing/index.html). You just need commands:
```
python -m pip install aioesphomeapi
python -m pip install asyncio
```

In case of existing modules check its versions. It should be `10.x` or newer for `aioesphomeapi` and `3.4` or newer for `asyncio`. If this isn't the case then update the modules:
```
pip3 install aioesphomeapi -U
pip3 install asyncio -U
```

When updating the `aioesphomeapi` module, it is possible to receive an error like this:
`ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.`
`esphome 2022.5.0 requires aioesphomeapi==10.8.2, but you have aioesphomeapi 10.10.0 which is incompatible.`
This isn't a problem. Just make sure that it reports aioesphomeapi version `10.x` or newer in the last row. Otherwise, update the esphome module:
```
pip3 install esphome -U
```

## Step 3: The logger ##
Download [logger script](https://raw.githubusercontent.com/GrKoR/ac_python_logger/main/ac_logger.py) to your local folder.

# How to use it #
## Uptodate help ##
For help use `-h` parameter. 
```
py ac_logger.py -h
```

## Run the script ##
Script has two required params:
- -i - IP address of the `ac_aux` device
- -p - Password of native esphome API for the `ac_aux` device 

The following minimal command will run script:
```
py ac_logger.py -i 192.168.0.1 -p MyCo0lPas$word
```

Script will work till you stop it by CTRL+C.
During the script execution you will see logger messages on the screen. Something like this:
```
noname,2021-06-02 22:22:22,0000123456,[<=],BB,00,01,00,00,00,00,00,43,FF
```

## Log file name ##
```
py ac_logger.py -i 192.168.0.1 -p MyCo0lPas$word -l common_data.csv
```
When you start script it creates new or open for append existing csv-file for writing data.

Default file name format is `YYYY-MM-DD hh-mm-ss log.csv`.

You can set filename as you wish by specifying `-l new_file_name.csv` command line parameter. If logfile exist script will append data to the end of the file.

## Device name ##
If you want to name your device in the log you should specify `-n NAME` command line parameter.
```
py ac_logger.py -i 192.168.0.1 -p MyCo0lPas$word -n ac_kitchen
```

This feature is very useful if you want capture logs from several independent AUX HVACs into the common log file. In case of logging a multisplit AC this feature is useful too.

Just run several ac_logger.py scripts with different parameters and the same logfile. It may looks like this:

console one:
```
py ac_logger.py -i 192.168.0.100 -p MyCo0lPas$word -n ac_kitchen -l common_log.csv
```

console two:
```
py ac_logger.py -i 192.168.0.101 -p MyCo0lPas$word -n ac_livingroom -l common_log.csv
```

Pay attention to identical logfile name for all consoles.


## Dallas temperature logging ##
If your `ac_aux` device has dallas DS18B20 sensors installed you can store it data to the logfile. Just set `-d` parameter of the script.
```
py ac_logger.py -i 192.168.50.12 -p MyCo0lPas$word -d
```

In that case script will capture all dallas data from the esphome log. It will store to the log following data:
- dallas temperature sensor name
- date and time of current sensor state
- temperature value

In the logfile dallas sensor generates records like this:
```
Outdoor Temperature;2021-12-15 17:22:17;;[<=];AA;4.4
```
Where
- `Outdoor Temperature` is a name of dallas sensor
- `2021-12-15 17:22:17` is date&time of event
- `[<=]` is data transfer direction
- `AA` is the custom record flag
- `4.4` is temperature value


## The results ##
Every time when logger receives data it will save it to CSV file. This file is located in the current folder.
You may open this file without script termination if your csv-viewer isn't locking csv-file. For example Notepad++.

Open file with Excell or LibreOffice for analyze. But before this you need to terminate script cause spreadsheet processor may lock the csv-file.

# Important notes #
## Script and esphome addon for Home Assistant ##
Users reports that there is an error in case of opening HA esphome addon log after script start:
```
Unexpected error while reading incoming messages: ...
...
AttributeError: 'NoneType' object has no attribute 'group'
```

This error isn't reproduced if you will start the script and then:
- view log in esp web-server;
- view log with `esphome logs your.yaml` console command. 
