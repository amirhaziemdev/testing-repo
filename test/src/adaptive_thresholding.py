'''
Created on 3 Jan 2019

@author: Amir Haziem Razali

Some chunks lifted from the Internet, forgot to cite them. If this looks like yours, message me!

This code is for testing the three thresholding methods, which are:
- global thresholding
- adaptive mean thresholding
- adaptive gaussian thresholding

Method for running:
on CMD navigate to directory with the python file and write:
python adaptive_thresholding.py --value <threshold value(optional, default=127)> --darkbg <True or False (optional, default=False)>
play around with the values until you get the right threshold value.
This is a quick way for trial and error of the art of thresholding ;)
'''
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import argparse
import time

#construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--value", type=int, help="set V threshold value")
ap.add_argument("-d", "--darkbg", type=str, help="set darkbg options True/False")
args = vars(ap.parse_args())

if not args.get("value", False):
    print("No threshold preference given.\nSetting default threshold value to 127...")
    v_thresh = 127
else:
    #otherwise, grab value set to flag
    v_thresh = args["value"]

if not args.get("darkbg", False):
    print("No darkbg preference given.\nSetting default darkbg to False...")
    darkbg = False
else:
    #otherwise, grab value set to flag
    darkbg = args["darkbg"]


img = cv.imread('cardoor_test_photos/cardoor-07-01-2019-14-29-21.jpg',0)
img = cv.medianBlur(img,5)
if not darkbg:
    ret,th1 = cv.threshold(img,v_thresh,255,cv.THRESH_BINARY)
else:
    ret,th1 = cv.threshold(img,v_thresh,255,cv.THRESH_BINARY_INV)
    
th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,\
            cv.THRESH_BINARY,11,2)
th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,11,2)
titles = ['Original Image', 'Global Thresholding (v = {})'.format(v_thresh),
            'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
images = [img, th1, th2, th3]
for i in range(4):
    plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
plt.show()