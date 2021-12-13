import time
import aioesphomeapi
import asyncio
import re
from aioesphomeapi.api_pb2 import (LOG_LEVEL_NONE,
                                   LOG_LEVEL_ERROR,
                                   LOG_LEVEL_WARN,
                                   LOG_LEVEL_INFO,
                                   LOG_LEVEL_DEBUG,
                                   LOG_LEVEL_VERBOSE,
                                   LOG_LEVEL_VERY_VERBOSE)

from secrets import AC_IP, AC_PASS

logFileName = "%4d-%02d-%02d %02d-%02d-%02d AC-DATA.csv" % time.localtime()[0:6]

async def main():
    """Connect to an ESPHome device and wait for state changes."""
    loop = asyncio.get_running_loop()
    api = aioesphomeapi.APIClient(loop, AC_IP, 6053, AC_PASS)

    await api.connect(login=True)

    print(api.api_version)

    def log_callback(log):
        """Print the log for AirCon"""
        isAirConLog = re.search("\[AirCon:\d+\]: (.+\])", log.message)
        if isAirConLog:
            """print(log.message)"""
            packString = '\n' + "%4d-%02d-%02d %02d:%02d:%02d" % time.localtime()[0:6]
            parts = re.search("(\d{10}): (\[\S{2}\]) \[([0-9A-F ]{23})\]\s?((?:[0-9A-F]{2}\s*)*) \[([0-9A-F ]{5})\]", isAirConLog.group(1))
            """millis of message"""
            packString += "," + parts.group(1)
            """direction"""
            packString += "," + parts.group(2)
            """header"""
            """packString += "," + ','.join(list(map(lambda x: int(x, 16), parts.group(3).split(" "))))"""
            packString += "," + ','.join(parts.group(3).split(" "))
            """body (may be void)"""
            if len(parts.group(4)) > 0:
                """packString += "," + ','.join(list(map(lambda x: int(x, 16), parts.group(4).split(" "))))"""
                packString += "," + ','.join(parts.group(4).split(" "))
            """crc"""
            """packString += "," + ','.join(list(map(lambda x: int(x, 16), parts.group(5).split(" "))))"""
            packString += "," + ','.join(parts.group(5).split(" "))
            print(packString)
            with open(logFileName, 'a+') as file:
                file.write( packString )

    # Subscribe to the log
    await api.subscribe_logs(log_callback, LOG_LEVEL_DEBUG)


loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.close()