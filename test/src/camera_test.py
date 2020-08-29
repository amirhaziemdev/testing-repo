'''
Created on 17 Dec 2018

@author: Amir Haziem Razali
'''

import numpy as np
import cv2
from imutils import contours
from skimage import measure
import imutils
import datetime
import time

#Switches
# camera = input('Please enter camera number, 0 for internal, 1 for external') #0 for internal webcam ;  #1 for external camera
camera = [0,1,-1]
flip = True #true if you want to flip the view
darkbg = True
overlay = True

#Thresholds
r_high = 7 #pixels
r_low = 4 #pixels
d = 15 #cm, this needs to be modified as appropriate
de = 40 #cm, distance from camera installation to surface
f = 0.375 #factor by which the distance from camera is multiplied

try:
    cap = cv2.VideoCapture(int(camera(0)))
except:
    print('No camera detected! Change camera index or connect a camera')

          
def main():
    while(True):
        
        # capture frame by frame
            ret, frame = cap.read()
            
            #operations on frame
#             hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            if(flip):
#                 hsv = cv2.flip(hsv, 1)
                frame = cv2.flip(frame, 1)
            
            #display resulting frame
            [x, y] = [25, 25]
            feed = dot_detection(frame)
            #dot detection code should go here, fed into "gray"
            
            if ret and camera == 1:
                cv2.putText(feed, 'Webcam feed', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0)
                cv2.imshow('Webcam Feed', feed)
    #             print('Camera size:', cap.get(3), 'x', cap.get(4))
            elif ret and camera == 0:
                cv2.putText(feed, 'Videocam feed', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0)
                cv2.imshow('Videocam Feed', feed)
            else:
                print('Camera feed error. Check webcam')
                break
            
            cv2.setMouseCallback('Webcam Feed', take_snapshot)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
            
        #release the capture
    cap.release()
    cv2.destroyAllWindows()
    return 0

def dot_detection(img):
    
    image = img
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (11,11), 0)
    if darkbg:
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
    else:
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
#     thresh = invert_colors(thresh)
    labels = measure.label(thresh, neighbors=8, background=0)
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
        
        if numPixels > 20 and numPixels < 200:
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
            
            if cX > 320:
                coordX = (cX - 320)/d
            else:
                coordX = -(320 - cX)/d
            coordY = (460 - cY)/d
            [coordX, coordY] = [round(coordX, 2), round(coordY, 2)]
            
            if overlay:
                cv2.putText(image, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.line(image, (0, 460), (640, 460), color = 255)
                cv2.line(image, (320, 0), (320, 480), color = 255)
                cv2.circle(image, (320, 460), 5, (255, 0, 0), 1)
            else:
                continue
    global feed
    # feed = gray
    # feed = thresh
    feed = image
    return feed

def invert_colors(img):
    img = abs(255 - img)
    return img

def take_snapshot(event, x, y, flage, param):
    if event==cv2.EVENT_LBUTTONDBLCLK:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')
        cv2.imwrite('Screenshot{}.jpg'.format(st), feed)

if __name__ == "__main__":
    main()