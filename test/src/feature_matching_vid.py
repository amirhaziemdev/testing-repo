'''
Created on 14 Feb 2019

@author: Amir Haziem Razali
Code for object tracking using Homography
Tutorial by Pysource on YouTube

Non-working due to patented algorithm for SIFT. Similar problem should occur if SURF is attempted
'''

import cv2
import numpy as np
from cv2 import waitKey

img_dir = 'feature_matching/feature_wholedoor'
img_dir = img_dir + '.jpg'

img = cv2.imread(img_dir, cv2.IMREAD_GRAYSCALE)

cap = cv2.VideoCapture(0)

#features
sift = cv2.xfeatures2d.SIFT_create()
kp_img, desc_img = sift.detectAndCompute(img, None)
img = cv2.drawKeypoints(img, kp_img, img)

while True:
    ret, frame = cap.read()
    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    kp_grayframe, desc_grayframe = sift.detectAndCompute(grayframe, None)
    
    cv2.imshow("image", img)
    if ret:
        cv2.imshow("frame", frame)
    
    key = 0xFF & waitKey(0)
    
    if key == ord('q'):
        break
    

cap.release()
cv2.destroyAllWindows()
