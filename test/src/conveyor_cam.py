'''
Created on 24 Dec 2018

@author: USER
'''

import numpy as np
import cv2
from imutils import contours
from skimage import measure 
import imutils
import datetime
import time

#camera select
# try: 
#     camera = input('Select camera feed, 0 for external, 1 for webcam') #select camera feed
# except:
#     print('No value selected, auto-assigned to external')
#     camera = 0

camera = 0
#Flags/switches
darkbg = False
overlay = True

#Thresholds
r_high = 1000
r_low = 12
pxthresh_low = 1
pxthresh_high = 20000
d = 15 #cm
de = 40 #cm
f = 0.375 #factor by which the distance is multiplied

try:
    cap = cv2.VideoCapture(int(camera))
except:
    print('No value selected, auto-assigned to external')
    cap = cv2.VideoCapture(0)

def main():
    
    while(True):
        
        ret, frame = cap.read()
        [x,y] = [25, 25]
        try:
            feed = mould_detection(frame)
        except:
            print('Error after threshold change!')
            break
    
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
    
    cap.release()
    cv2.destroyAllWindows()
    return 0

def mould_detection(frame):
    image = frame
    global feed
    feed = frame
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    if darkbg:
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
    else:
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
    
    labels = measure.label(thresh, neighbors=8, background=0)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    thresh = th3
    mask = np.zeros(thresh.shape, dtype="uint8")
    
    #loop over unique components
    for label in np.unique(labels):
        #ignores background labels
        if label == 0:
            continue
        #otherwise, construct label mask and count pixels
        labelMask = np.zeros(thresh.shape, dtype = "uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        #if the number of pixels in the component is small enough
        # then add it to our mask of small blobs
        
        if numPixels > pxthresh_low and numPixels < pxthresh_high:
            mask = cv2.add(mask, labelMask)
            
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    try:
        cnts = contours.sort_contours(cnts)[0]
    except:
        print("No holes detected!")
    #loop over contours
    for i, c in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        
#         if radius > r_high or radius < r_low:
#             cnts[i] = 0
        if radius < r_high and radius > r_low:
            if overlay:
                cv2.circle(image, (int(cX), int(cY)), int(radius), (0,0,255), 3)
                print("circle no. {}".format(i+1), "radius:", radius, "center:", cX, ",", cY)
                cv2.putText(image, "hole # {}".format(i+1), (x,y -15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 2)
                cv2.rectangle(image, (int(cX-(w/2)), int(cY-(h/2))), (int(cX+(w/2)), int(cY+(h/2))), (255,0,0), 2)
        
            if cX > 320:
                coordX = (cX - 320)/d
            else:
                coordX = -(320 - cX)/d
        
            coordY = (460 - cY)/d
            [coordX, coordY] = [round(coordX, 2), round(coordY, 2)]
            #converting h,w to real sizes from pixel size
            [h,w] = [round(h/d, 2), round(w/d, 2)]
            area = round(h*w, 2)
            if overlay:
                cv2.putText(image, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.putText(image, "height and width: ({},{})".format(h, w), (int(cX - radius),int(cY +radius) + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.putText(image, "area: ({})".format(area), (int(cX - radius),int(cY +radius) + 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.line(image, (0, 460), (640, 460), color = 255)
                cv2.line(image, (320, 0), (320, 480), color = 255)
                cv2.circle(image, (320, 460), 5, (255, 0, 0), 1)
                feed = image
            else:
                cv2.putText(thresh, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.line(thresh, (0, 460), (640, 460), color = 255)
                cv2.line(thresh, (320, 0), (320, 480), color = 255)
                cv2.circle(thresh, (320, 460), 5, (255, 0, 0), 1)
                feed = thresh

    
    return feed

def take_snapshot(event, x, y, flage, param):
    if event==cv2.EVENT_LBUTTONDBLCLK:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%d%m%Y%H%M%S')
        cv2.imwrite('Screenshot_{}.jpg'.format(st), feed)

def show_feed():
    
    
    
    
    return 0



if __name__ == '__main__':
    main()
