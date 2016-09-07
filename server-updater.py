# Watches the temperature of the CPU
# using the python pysensors package using a sockets to
# do a handshake with the server.
# Author: Garth Toland
# Date: 09/08/2016

import sensors
import time
from socketIO_client import SocketIO, LoggingNamespace
import datetime
import request

past_data = 0


def print_as_json():
    print('\n{"Core 0":%s,'
          '\n"Core 1": %s,'
          '\n"Fan 1": %s,'
          '\n"Fan 2": %s,'
          '\n"Fan 4": %s,'
          '\n"System temp": %s,'
          '\n"Power Supply temp": %s,'
          '\n"CPU temp (MB)": %s}'
          % (core0, core1, fan1, fan2, fan4, systin, auxtin, cputin))


def print_to_screen():
    print('\nCore 0: %s '
          '\nCore 1: %s'
          '\nFan 1: %s'
          '\nFan 2: %s'
          '\nFan 4: %s'
          '\nSystem temp: %s'
          '\nPower Supply temp: %s'
          '\nCPU temp (MB): %s'
          % (core0, core1, fan1, fan2, fan4, systin, auxtin, cputin))


def get_time():
    return datetime.datetime.now().time()


# Send data through socket, only if data was different.
def send_data(data):
    global past_data
    if past_data != data:
        with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:
            socketIO.emit('server-status-update', {'cpu_temperature': data})
            print("Data: " + str(data) + " @ " + str(get_time()))
    past_data = data


print("Started @ " + str(get_time()))
while True:
    sensors.init()
    try:
        for chip in sensors.iter_detected_chips():
            # print('%s at %s' % (chip, chip.adapter_name))
            for feature in chip:
                if feature.label == 'fan1':
                    fan1 = feature.get_value()
                elif feature.label == 'fan2':
                    fan2 = feature.get_value()
                elif feature.label == 'fan4':
                    fan4 = feature.get_value()
                elif feature.label == 'Core 0':
                    core0 = feature.get_value()
                elif feature.label == 'Core 1':
                    core1 = feature.get_value()
                elif feature.label == 'SYSTIN':  # core avg temp
                    systin = feature.get_value()
                elif feature.label == 'AUXTIN':  # power supply temp
                    auxtin = feature.get_value()
                elif feature.label == 'CPUTIN':  # motherboard cpu temp
                    cputin = feature.get_value()
    finally:
        # print_to_screen()
        send_data(core0)
        # sensors.cleanup()
        time.sleep(0.05)

print("Finished @ " + str(get_time()))
