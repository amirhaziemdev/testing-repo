'''
Created on 18 Feb 2019

@author: Amir Haziem Razali
Testing IP camera stream (ONVIF) using urllib
'''

import urllib.request
import cv2
import numpy as np

cv2.namedWindow('IP Camera')
# streamAdd = 'rtp://192.168.1.208:5004' #RTP/AVP stream
streamAdd = "http://localhost:8080/test" #HTTP stream
# streamAdd = "udp://192.168.1.209:1234" #UDP streaming
# streamAdd = "test.mp4" #MP4 container (dynamic, moov atom not found error)
''' using urllib'''
urlresp = urllib.request.urlopen(streamAdd)
# urlresp = urllib.request.FancyURLopener({"http":"http://127.0.0.1:8080"}).open(streamAdd).read().decode("utf-8")
imgNp = np.array(bytearray(urlresp.read()), dtype=np.uint8)
img = cv2.imdecode(imgNp,-1)

'''using cv2.VideoCapture'''
# stream = cv2.VideoCapture(streamAdd)
while True:
    print("Streaming...")
#     ret,img = stream.read()
    cv2.imshow('IP Camera', img)
    

cv2.waitKey(0)