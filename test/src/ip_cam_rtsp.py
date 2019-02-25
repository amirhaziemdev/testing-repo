'''
Created on 8 Feb 2019

@author: Amir Haziem Razali
Getting rtsp IP camera feed using python's rtsp import


'rtsp://192.168.1.207:554/onvif1'
'''
import rtsp
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

print('Attempting connection...')
with rtsp.Client(rtsp_server_uri = 'rtsp://192.168.1.207:554/onvif1') as client:
    while True:
        _image = client.read()
        _image.show()