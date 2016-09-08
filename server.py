# Python Server #
import socketio
import eventlet
import eventlet.wsgi
import json
import time
import threading
from flask import Flask, render_template
from gcm import GCM

sio = socketio.Server()
app = Flask(__name__)
sid_array = []
threads = []
API_KEY = ''  # Google API Key
reg_ids = []  # Registration Ids


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

        # deploy as an eventlet WSGI server
        eventlet.wsgi.server(eventlet.listen(('', 8000)), app)


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
    if core0 > 60:
        print("It is greater than 60!")
        send_message(reg_ids)


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


# ////////////////// Main Program //////////////////////// #

server_thread = Server("Server-thread")
server_thread.start()
threads.append(server_thread)
