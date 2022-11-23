import time
import aioesphomeapi
import asyncio
import re
import argparse
from aioesphomeapi.api_pb2 import (LOG_LEVEL_NONE,
                                   LOG_LEVEL_ERROR,
                                   LOG_LEVEL_WARN,
                                   LOG_LEVEL_INFO,
                                   LOG_LEVEL_DEBUG,
                                   LOG_LEVEL_VERBOSE,
                                   LOG_LEVEL_VERY_VERBOSE)

def createParser ():
    parser = argparse.ArgumentParser(
        description='''This script is used for collecting logs from ac_aux ESPHome component.
                       For more info, see https://github.com/GrKoR/ac_python_logger''',
        add_help = False)
    parent_group = parser.add_argument_group (title='Params')
    parent_group.add_argument ('--help', '-h', action='help', help='show this help message and exit')
    parent_group.add_argument ('-i', '--ip', nargs=1, required=True, help='IP address of the esphome device')
    parent_group.add_argument ('-p', '--pwd', nargs=1, required=True, help='native API password for the esphome device')
    parent_group.add_argument ('-n', '--name', nargs=1, default=['noname'], help='name of this devace in the log')
    parent_group.add_argument ('-l', '--logfile', nargs=1, default=['%4d-%02d-%02d %02d-%02d-%02d log.csv' % time.localtime()[0:6]], help='log file name')
    parent_group.add_argument ('-d', '--logdallas', action='store_true', default=False, help='Whether or not to save the outdoor temperature to the log. Script will try to find dallas.sensor output in the esphome api. If there are several dallas sensors in the esp device all of them will be stored in the log.')
    parent_group.add_argument ('-g', '--logping', action='store_true', default=False, help='Whether or not to save the ping messages to the log.')
    return parser

async def main():
    """Connect to an ESPHome device and wait for state changes."""
    api = aioesphomeapi.APIClient(namespace.ip[0], 6053, namespace.pwd[0])

    try:
        await api.connect(login=True)
    except aioesphomeapi.InvalidAuthAPIError as e:
        return print(e)

    print(api.api_version)

    def log_AC(isAirConLog):
        parts = re.search("(\d{10}): (\[\S{2}\]) \[([0-9A-F ]{23})\]\s?((?:[0-9A-F]{2}\s*)*) \[([0-9A-F ]{5})\]", isAirConLog.group(1))
        packString = '\n' + namespace.name[0]
        packString += ";" + "%4d-%02d-%02d %02d:%02d:%02d" % time.localtime()[0:6]
        """millis of message"""
        packString += ";" + parts.group(1)
        """direction"""
        packString += ";" + parts.group(2)
        """header"""
        header_list = parts.group(3).split(" ")
        is_ping = (header_list[2] == "01")
        packString += ";" + ';'.join(header_list)
        """body (may be void)"""
        if len(parts.group(4)) > 0:
            packString += ";" + ';'.join(parts.group(4).split(" "))
        """crc"""
        packString += ";" + ';'.join(parts.group(5).split(" "))
        print(packString)
        
        if is_ping:
            if namespace.logping:
                with open(namespace.logfile[0], 'a+') as file:
                    file.write( packString )
            else:
                print("ping skipped")
        else:
            with open(namespace.logfile[0], 'a+') as file:
                file.write( packString )

    def log_Dallas(isDallasLog):
        parts = re.search("'([\w ]+)': Got Temperature=([-]?\d+\.\d+)°C", isDallasLog.group(1))
        packString = '\n' + parts.group(1)
        packString += ";" + "%4d-%02d-%02d %02d:%02d:%02d" % time.localtime()[0:6]
        """millis of message always empty"""
        packString += ";"
        """direction"""
        packString += ";[<=]"
        """additional data flag"""
        packString += ";AA"
        """dallas temperature"""
        packString += ";" + parts.group(2)
        print(packString)
        with open(namespace.logfile[0], 'a+') as file:
            file.write( packString )

    def log_callback(log):
        """Print the log for AirCon"""
        isAirConLog = re.search("\[AirCon:\d+\]: (.+\])", log.message.decode('utf-8'))
        if isAirConLog:
            log_AC(isAirConLog)
        if namespace.logdallas:
            isDallasLog = re.search("\[dallas.sensor:\d+\]: (.+C)", log.message.decode('utf-8'))
            if isDallasLog:
                log_Dallas(isDallasLog)


    # Subscribe to the log
    await api.subscribe_logs(log_callback, LOG_LEVEL_DEBUG)


if __name__ == "__main__":
    parser = createParser()
    namespace = parser.parse_args()
    print(namespace.name[0], namespace.ip[0])


    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.ensure_future(main(), loop=loop)
        loop.run_forever()
    except aioesphomeapi.InvalidAuthAPIError as e:
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        pass