# import the necessary packages
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import requests
import argparse
import datetime
import random
import imutils
import json
import time
import cv2
import numpy as np

class FrameGetter:
    def __init__(self, map_path):

        self._api_key = '5871aee18a546aecf2a8ef5cecbfd178'
        self._frame = 0
        self._last_frame = 0
        self._frames_since_last_request = 201
        self._mapping = json.load(open(map_path))

    def _get_temp(self, place):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "appid=" + self._api_key + "&q=" + place 
        response = requests.get(complete_url) 
        x = response.json() 
        if x["cod"] != "404": 
            y = x["main"] 
            print (y)
            return y["temp"] - 273.15
    
    def _open_video(self, path):
        print('oppe')
        self.cap = cv2.VideoCapture(path)

    def _get_frame_from_temp(self, temp):

        self._frame = -1 
        while self._frame == -1:
            temp = round(temp, 1)
            if str(temp) in self._mapping:
                self._frame, self._last_frame = random.choice(list(self._mapping[str(temp)].items())) 
                self._frame = int(self._frame)
                return self._frame, self._last_frame
            if '-' + str(temp) in self._mapping:
                self._frame, self._last_frame = random.choice(list(self._mapping['-' + str(temp)].items())) 
                self._frame = int(self._frame)
                return self._frame, self._last_frame
            temp += 0.1

    def _get_frame(self):
        
        if self._frames_since_last_request > 500 or self._frame > self._last_frame:
            temp = self._get_temp('sao+carlos')
            print (temp)
            self._get_frame_from_temp(temp)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self._frame)
            self._frames_since_last_request=0
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self._frame)
            self._frames_since_last_request+=1
        
        _, frame = self.cap.read()
        return frame

    def next_frame(self):
        self._frame += 1
        frame = self._get_frame()
        return frame

app = Flask(__name__)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def generate():
    getter = FrameGetter('result.json')
    getter._open_video('bread.mp4')
    # loop over frames from the output stream
    while True:
        outputFrame = getter.next_frame() 
        # img=np.array(np.rot90(outputFrame,-1))
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
        if not flag:
            continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

# check to see if this is the main thread of execution
if __name__ == '__main__':

    # print (next(generate()))
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	args = vars(ap.parse_args())
	
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=True,
		threaded=True, use_reloader=False)