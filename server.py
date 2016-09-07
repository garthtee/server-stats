# Python Server #
import socketio
import eventlet
import eventlet.wsgi
import ssl
import json
from flask import Flask, render_template

sio = socketio.Server()
app = Flask(__name__)


@app.route('/')
def index():
    """Serve the client-side application."""
    print("Welcome")
    return 'index.html'


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)


@sio.on('serverStatusUpdate')
def message(sid, data):
    data = str(data)
    n = json.dumps(data)
    json_data = json.loads(n)
    core0 = json_data.partition("core0': u'")[-1].rpartition("', u'core1")[0]
    core1 = json_data.partition("core1': u'")[-1].rpartition("'")[0]
    print("*********")
    print(core0)
    print(core1)
    print("*********")


@sio.on('chat message')
def message(sid, data):
    print("message ", data)
    sio.emit('reply', room=sid)


@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    # wrap Flask application with engineio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

# if __name__ == "__main__":
#     app = socketio.Middleware(sio, app)
#     context = ('cert.pem', 'privkey.pem')
#     app.run(host='0.0.0.0', port=8000, ssl_context=context, threaded=True, debug=True)
