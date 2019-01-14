'''
Created on 3 Jan 2019

@author: Amir Haziem Razali

Code for detecting molds on conveyor
'''


import cv2
import numpy as np
import imutils
from imutils import contours
from skimage import measure

dir_img = "test_photos/IMG_0578.jpg"

img = cv2.imread(dir_img)
img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
height, width, channels = img.shape
print(height, width, channels)

#Flags/switches
darkbg = True
overlay = True

#constants
cam_width = width
cam_height = height
textSize = 1.0

#Thresholds
v_thresh = 150 #v value for threshold function
multiplier = 10 #to adjust for different camera resolutions
axis_offset = 100
r_high = 1000
r_low = 12
pxthresh_low = 1
pxthresh_high = 20000
d = 15 #cm
de = 40 #cm
f = 0.375 #factor by which the distance is multiplied


def main():
#     img = mould_detection(img)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    ret3,th3 = cv2.threshold(blur,v_thresh,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    proc = mould_detection(img)
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", proc)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return 0

def mould_detection(frame):
    image = frame
    global feed #ugly debug, get rid of this ASAP
    feed = frame
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if darkbg:
        thresh = cv2.threshold(gray, v_thresh, 255, cv2.THRESH_BINARY)[1]
    else:
        thresh = cv2.threshold(gray, v_thresh, 255, cv2.THRESH_BINARY_INV)[1]
    
    labels = measure.label(thresh, neighbors=8, background=0)
#     blur = cv2.GaussianBlur(gray,(5,5),0)
#     ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#     thresh = th3
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
        if numPixels > pxthresh_low*multiplier and numPixels < pxthresh_high*multiplier:
            mask = cv2.add(mask, labelMask)
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    try:
        cnts = contours.sort_contours(cnts)[0]
    except:
        print("No holes detected!")
    #loop over contours
    j = 0
    for i, c in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        if radius < r_high*multiplier and radius > r_low*multiplier:
            if overlay:
                #omit drawing a circle, don't need it for conveyor
#                 cv2.circle(image, (int(cX), int(cY)), int(radius), (0,0,255), 3)
                print("circle no. {}".format(j+1), "radius:", radius, "center:", cX, ",", cY)
                cv2.putText(image, "mold # {}".format(j+1), (x,y -15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 2)
                cv2.rectangle(image, (int(cX-(w/2)), int(cY-(h/2))), (int(cX+(w/2)), int(cY+(h/2))), (255,0,0), 2)
                j=j+1
            if cX > (cam_width/2):
                coordX = (cX - (cam_width/2))/d
            else:
                coordX = -((cam_width/2) - cX)/d
        
            coordY = ((cam_height-20) - cY)/d
            [coordX, coordY] = [round(coordX, 2), round(coordY, 2)]
            #converting h,w to real sizes from pixel size
            [h,w] = [round(h/d, 2), round(w/d, 2)]
            area = round(h*w, 2)
            if overlay:
                cv2.putText(image, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.putText(image, "height and width: ({},{})".format(h, w), (int(cX - radius),int(cY +radius) + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.putText(image, "area: ({})".format(area), (int(cX - radius),int(cY +radius) + 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                cv2.line(image, (0, cam_height-axis_offset), (cam_width, cam_height-axis_offset), color = 255) #horizontal line/axis
                cv2.line(image, (int(cam_width/2), 0), (int(cam_width/2), int(cam_height)), color = 255) #vertical axis
                cv2.circle(image, (int(cam_width/2), cam_height-axis_offset), 50, (255, 0, 0), 1)
                feed = image
            else:
                cv2.line(image, (0, cam_height-axis_offset), (cam_width, cam_height-axis_offset), color = 255) #horizontal line/axis
                cv2.line(image, (int(cam_width/2), 0), (int(cam_width/2), int(cam_height)), color = 255) #vertical axis
                cv2.circle(image, (int(cam_width/2), cam_height-axis_offset), 50, (255, 0, 0), 1)
                feed = thresh
    return feed

if __name__=="__main__":
    main()
