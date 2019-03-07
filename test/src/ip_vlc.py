'''
Created on 16 Feb 2019

@author: Amir Haziem Razali

This code utilises the python-vlc toolbox and can successfully play a RTSP stream for Yoosee camera, URL: "rtsp://192.168.1.206:554/onvif1"
Just like VLC media player, this toolbox can play streams with a ~2 seconds latency. Should be okay for conveyor implementation

16/2/2019 12:30pm
The plan now is to intercept the frames every few milliseconds for image processing using OpenCV.

'''


import vlc
import cv2

key = 0xFF & cv2.waitKey(0) 

streamAdd = "rtsp://192.168.1.206:554/onvif1" #this one works in cmd (Yoosee)

player = vlc.MediaPlayer("rtsp://192.168.1.206:554/onvif1")
player.play()

while player.is_playing():
    if key == ord('q'):
        break
    
player.stop()
player.release()