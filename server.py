# Python Server #
import socketio
import eventlet
import eventlet.wsgi
import json
import threading
import sensors
import time
import datetime
import urllib3
import psutil
from urllib3.exceptions import InsecureRequestWarning
from socketIO_client import SocketIO, LoggingNamespace
from flask import Flask, render_template
from gcm import GCM

# SocketIO #
urllib3.disable_warnings(InsecureRequestWarning)
past_core0 = 0
past_core1 = 0
past_cpu_usage = 0

# GCM #
sio = socketio.Server()
app = Flask(__name__)
sid_array = []
threads = []
API_KEY = ''  # Google API Key
reg_ids = ['']  # Registration Ids


class Server(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.threadID = thread_id

    def run(self):
        print("Starting " + self.name)
        serve()
        print("Exiting " + self.name)


def serve():
    if __name__ == '__main__':
        global app
        # wrap Flask application with engineio's middleware
        app = socketio.Middleware(sio, app)

        eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('', 8000)),
                                               certfile='/home/garthtee/cert.pem',
                                               keyfile='/home/garthtee/privkey.pem'), app)


def send_message(reg_ids):
    gcm = GCM(API_KEY)
    data = {'message': 'Hello from python!'}

    # Downstream message using JSON request
    response = gcm.json_request(registration_ids=reg_ids, data=data)

    # Successfully handled registration_ids
    if 'success' in response:
        print(response)
        for reg_id, success_id in response['success'].items():
            print('Successfully sent notification for reg_id {0}'.format(reg_id))

    # Handling errors
    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            print("Unsuccessful. ERROR = " + str(response['errors']))
            # Check for errors and act accordingly
            if error in ['NotRegistered', 'InvalidRegistration']:
                # Remove reg_ids from database
                for reg_id in reg_ids:
                    print("Removing reg_id: {0} from db".format(reg_id))


@app.route('/')
def index():
    # Serve the client-side application
    users = len(sid_array)
    return "There is " + str(users) + " users."


@sio.on('connect')
def connect(sid, environ):
    sid_array.append(sid)
    users = len(sid_array)
    print("There is " + str(users) + " users.")


@sio.on('serverStatusUpdate')
def message(sid, data):
    data = str(data)
    n = json.dumps(data)
    json_data = json.loads(n)
    core0 = json_data.partition("core0': u'")[-1].rpartition("', u'core1")[0]
    core0 = int(core0)
    core1 = json_data.partition("core1': u'")[-1].rpartition("'")[0]
    core1 = int(core1)
    print("*********")
    print(str(core0))
    print(str(core1))
    print("*********")
    send_message(reg_ids)


@sio.on('hi')
def hi(sid):
    sio.emit('status-update', {'core0_in': core0, 'core1_in': core1, 'cpu_usage_in': cpu_usage})


@sio.on('chat message')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)


@sio.on('disconnect')
def disconnect(sid):
    sid_array.remove(sid)
    users = len(sid_array)
    print("There is " + str(users) + " users left.")
    print('Disconnected')


def get_time():
    return datetime.datetime.now().time()


# ////////////////// Main Program //////////////////////// #

server_thread = Server("Server-thread")
server_thread.start()
threads.append(server_thread)
print("Started @ " + str(get_time()))
count = 0
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
        sensors.cleanup()
        time.sleep(2)


        #    if __name__ == '__main__':
        #         global app
        #         # wrap Flask application with engineio's middleware
        #         app = socketio.Middleware(sio, app)
        #
        #         # deploy as an eventlet WSGI server
        #         eventlet.wsgi.server(eventlet.listen(

        # if past_core0 != core0 or past_core1 != core1 or past_cpu_usage != cpu_usage:
        #     sio.emit('status-update', {'core0_in': core0, 'core1_in': core1, 'cpu_usage_in': cpu_usage})
        #     count += 1
        #     print("Emitted. Count = " + str(count))
        # past_core0 = core0
        # past_core1 = core1
        # past_cpu_usage = cpu_usage
