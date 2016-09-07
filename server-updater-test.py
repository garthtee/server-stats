# Watches the temperature of the CPU
# using the python pysensors package using a sockets to
# do a handshake with the server.
# Author: Garth Toland
# Date: 09/08/2016

# Don't have any 'u' in emits #

import sensors
import time
from socketIO_client import SocketIO, LoggingNamespace
import datetime
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

past_core0 = 0
past_core1 = 0
past_cpu_usage = 0
socketIO = SocketIO('http://127.0.0.1:8000')

def get_time():
    return datetime.datetime.now().time()


# Send data through socket, only if data was different.
def send_data(count_in):
    socketIO.emit('serverStatusUpdate', {'core0': str(count_in), 'core1': str(count_in + 1)})
    print("Sent -> " + str(count_in))


print("Started @ " + str(get_time()))
count = 0
while True:
    count += 1
    send_data(count)
    time.sleep(2)

