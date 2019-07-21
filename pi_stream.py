#!/usr/bin/env python

import picamera
import time
import io
import os

from flask import Flask, Response, render_template
from flask_basicauth import BasicAuth


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.environ['STREAMUSER']
app.config['BASIC_AUTH_PASSWORD'] = os.environ['STREAMPWD']

basic_auth = BasicAuth(app)


@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')


@app.route('/feed')
@basic_auth.required
def feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen():
    # video stream generator function
    while True:
        try:
            time.sleep(2)   # wait for focus
            stream = io.BytesIO()

            for _ in picamera.PiCamera().capture_continuous(stream, 'jpeg', use_video_port=True):
                stream.seek(0)

                yield(b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n')

                stream.seek(0)
                stream.truncate

        except Exception as e:
            print(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
