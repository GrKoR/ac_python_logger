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


def createParser():
    parser = argparse.ArgumentParser(
        description='''This script is used for collecting logs from ac_aux ESPHome component.
                       For more info, see https://github.com/GrKoR/ac_python_logger''',
        add_help=False)
    parent_group = parser.add_argument_group(title='Params')
    parent_group.add_argument('--help', '-h', action='help', help='show this help message and exit')
    parent_group.add_argument('-i', '--ip', nargs=1, required=True, help='IP address of the esphome device')
    parent_group.add_argument('-p', '--pwd', nargs=1, help='native API password for the esphome device')
    parent_group.add_argument('-e', '--encryption_key', nargs=1, help='native API enkription key')
    parent_group.add_argument('-n', '--name', nargs=1, default=['noname'], help='name of this devace in the log')
    parent_group.add_argument('-l', '--logfile', nargs=1, default=['%4d-%02d-%02d %02d-%02d-%02d log.csv' % time.localtime()[0:6]], help='log file name')
    parent_group.add_argument('-d', '--logdallas', action='store_true', default=False, help='Whether or not to save the outdoor temperature to the log. Script will try to find dallas.sensor output in the esphome api. If there are several dallas sensors in the esp device all of them will be stored in the log.')
    parent_group.add_argument('-g', '--logping', action='store_true', default=False, help='Whether or not to save the ping messages to the log.')
    return parser


async def main():
    """Connect to an ESPHome device and wait for state changes."""
    api = aioesphomeapi.APIClient(address=namespace.ip, port=6053,
                                  password=namespace.pwd,
                                  noise_psk=namespace.encryption_key)

    try:
        await api.connect(login=True)
    except (aioesphomeapi.InvalidAuthAPIError,
            aioesphomeapi.InvalidEncryptionKeyAPIError,
            aioesphomeapi.RequiresEncryptionAPIError) as e:
        return print(e)

    print(api.api_version)

    def log_AC(logstring: str):
        parts = re.search(
            r"(\d{10}): (\[\S{2}\]) \[([0-9A-F ]{23})\]\s?((?:[0-9A-F]{2}\s*)*) \[([0-9A-F ]{5})\]",
            logstring)
        packString = '\n' + namespace.name
        packString += ";" + \
            "%4d-%02d-%02d %02d:%02d:%02d" % time.localtime()[0:6]
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
                with open(namespace.logfile, 'a+') as file:
                    file.write(packString)
            else:
                print("ping skipped")
        else:
            with open(namespace.logfile, 'a+') as file:
                file.write(packString)

    def log_Dallas(isDallasLog):
        parts = re.search(
            r"'([\w ]+)': Got Temperature=([-]?\d+\.\d+)°C",
            isDallasLog.group(1))
        packString = '\n' + parts.group(1)
        packString += ";" + \
            "%4d-%02d-%02d %02d:%02d:%02d" % time.localtime()[0:6]
        """millis of message always empty"""
        packString += ";"
        """direction"""
        packString += ";[<=]"
        """additional data flag"""
        packString += ";AA"
        """dallas temperature"""
        packString += ";" + parts.group(2)
        print(packString)
        with open(namespace.logfile, 'a+') as file:
            file.write(packString)

    def log_callback(log):
        """Print the log for AirCon"""
        isAirConLog = re.search(
            r"\[AirCon:\d+\]: (.+\])", log.message.decode('utf-8'))
        if isAirConLog:
            logstring = isAirConLog.group(1)
            if re.match(r"^\d{10}: ", logstring) is None:
                logstring = "0000000000: " + logstring
            log_AC(logstring)
        if namespace.logdallas:
            isDallasLog = re.search(
                r"\[dallas.sensor:\d+\]: (.+C)", log.message.decode('utf-8'))
            if isDallasLog:
                log_Dallas(isDallasLog)

    # Subscribe to the log
    api.subscribe_logs(log_callback, LOG_LEVEL_DEBUG)


if __name__ == "__main__":
    parser = createParser()
    namespace = parser.parse_args()
    namespace.name = namespace.name[0].strip()
    namespace.ip = namespace.ip[0].strip()
    if namespace.pwd is not None:
        namespace.pwd = namespace.pwd[0].strip()
    if namespace.encryption_key is not None:
        namespace.encryption_key = namespace.encryption_key[0].strip()
    namespace.logfile = namespace.logfile[0].strip()
    print(namespace.name, "at", namespace.ip)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.ensure_future(main(), loop=loop)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()