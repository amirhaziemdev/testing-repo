'''
Created on 22 Jan 2019

@author: Amir Haziem Razali

Code for testing IP camera connection and display. Current settings as of 9:04AM 22/1/2019:
IP Address:      192.168.0.206
DNS:             192.168.1.1
Default gateway: 192.168.1.1
Subnet mask:     255.255.255.0

This code will attempt to connect to this camera and display the camera feed
PORT NUMBER IS UNKOWN, FOR NOW TRY USING 555

First attempt is direct connection to the device (connected to WiFi) using this method:
cap = cv2.VideoCapture('http://<user>:<pass>@<addr>:<port>/videostream.cgi?.mjpg')
Default port number taken, which is 80. Could be 3333 or 5000 ?

From iSpy website (http://www.ispyconnect.com/man.aspx?n=Shenzhen) or (http://www.ispyconnect.com/man.aspx?n=Shenzhen+Toptech), it is 
found that the PATH has a 'live/ch00_0' extension instead of 'videostream.cgi?'
Product is found to be from Shenzhen, named V380. 
Additional specs can be found from the Golden Vision China website: http://www.goldenvisionchina.com/-Fisheye-camera/r-26.html

Yoosee: rtsp://192.168.1.206:554/onvif1 (works with VLC media player, albeit a bit spotty. Got transport error with UDP/TCP stuff in code)
Xiami Mijia: rtsp://192..168.1.154:<port>/live/ch00_0

'''

import numpy as np
import cv2
import os
import sys

import base64
import urllib
from urllib.request import urlopen
from urllib.request import Request


key = cv2.waitKey(0) & 0xFF


streamAdd = "rtsp://192.168.1.206:554/onvif1"

class ipCamera(object):
    def __init__(self,url, user=None, password=None):
        self.url = url
        to_encode = '%s:%s' % (user,password)
        to_encode = bytes(to_encode, 'utf-8')
        auth_encoded = base64.encodestring(to_encode)[:-1]
        print(auth_encoded, type(auth_encoded))
        
        self.req = Request(self.url)
        self.req.add_header('Authorization', 'Basic %s' % auth_encoded)
        
    def get_frame(self):
        response = urlopen(self.req)
        img_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_array,1)
        return frame
    
def alt_main():
    cam = ipCamera(streamAdd, user='', password='')
    cv2.namedWindow("Display")
    while True:
        if cam.get_frame() != None:
            cv2.imshow("Display", cam.get_frame())
            
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()
    return 0

def main():
#     os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
#     print(os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"])
    print('Attempting connection...', streamAdd)
    cap = cv2.VideoCapture(streamAdd, apiPreference = cv2.CAP_GSTREAMER)
    cv2.namedWindow('IP Camera Feed', cv2.WINDOW_AUTOSIZE)
    if not cap.isOpened():
        print("Open RTSP link unsuccessful\n", sys.exc_info()[0])
    
    else:
        while True:
            ret,frame = cap.read()
            if not ret:
                print('Variable frame is empty')
                break
            else:
                print('Read successful! Displaying...')
                cv2.imshow('IP Camera Feed',frame)
    
            if key == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    return 0



if __name__=="__main__":
    main()