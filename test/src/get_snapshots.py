'''
Created on 26 Dec 2018

@author: USER
'''
import cv2
import numpy as np
import time
import datetime
import imutils


camera = 0

cap = cv2.VideoCapture(int(camera))

def main():
    
    while(True):
        ret, frame = cap.read()
        global feed
        feed = frame
        
        if ret and camera == 1:
#             cv2.putText(feed, 'Webcam feed', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0)
            cv2.imshow('Webcam Feed', feed)
    #             print('Camera size:', cap.get(3), 'x', cap.get(4))
        elif ret and (camera == 0 or camera == ''):
#             cv2.putText(feed, 'Videocam feed', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0)
            cv2.imshow('Videocam Feed', feed)
        else:
            print('Camera feed error. Check webcam')
            break
    
        cv2.setMouseCallback('Videocam Feed', take_snapshot)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    return 0;

def take_snapshot(event, x, y, flage, param):
    if event==cv2.EVENT_LBUTTONDBLCLK:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%d%m%Y%H%M%S')
        cv2.imwrite('Test_Screenshot_{}.jpg'.format(st), feed)

def show_feed():
    
    
    
    
    return 0



if __name__ == '__main__':
    main()