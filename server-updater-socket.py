# Watches the temperature of the CPU
# using the python pysensors package using a sockets to
# do a handshake with the server.
# Author: Garth Toland
# Date: 09/08/2016

import sensors
import time
from socketIO_client import SocketIO, LoggingNamespace
import datetime
import urllib3
import psutil
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

past_core0 = 0
past_core1 = 0
past_cpu_usage = 0
socketIO = SocketIO('https://127.0.0.1:3000', verify=False)


# socketIO = SocketIO('https://127.0.0.1',3000,verify='privkey.pem',cert=('cert.pem', 'chain.pem'))


def get_time():
    return datetime.datetime.now().time()


# Send data through socket, only if data was different.
def send_data(core0_in, core1_in, cpu_usage_in):
    global past_core0
    global past_core1
    global past_cpu_usage
    if past_core0 != core0_in or past_core1 != core1_in or past_cpu_usage != cpu_usage_in:
        socketIO.emit('server-status-update',
                      {'core0': core0_in, 'core1': core1_in, 'cpu_usage': cpu_usage_in})
    past_core0 = core0_in
    past_core1 = core1_in
    past_cpu_usage = cpu_usage_in


print("Started @ " + str(get_time()))
while True:
    sensors.init()
    try:
        for chip in sensors.iter_detected_chips():
            # print('%s at %s' % (chip, chip.adapter_name))
            for feature in chip:
                if feature.label == 'Core 0':
                    core0 = feature.get_value()
                elif feature.label == 'Core 1':
                    core1 = feature.get_value()
        for x in range(1):
            cpu_usage = str(psutil.cpu_percent(interval=1))
    finally:
        send_data(core0, core1, cpu_usage)
        sensors.cleanup()
        time.sleep(0.5)

