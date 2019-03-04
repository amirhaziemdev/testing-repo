'''
Created on 19 Feb 2019

@author: sentdex on Youtube: https://www.youtube.com/watch?v=2CZltXv-Gpk

Code for template matching
'''
import cv2
import numpy as np

img_bgr = cv2.imread('feature_matching/Test_Screenshot_14022019091656.jpg')
img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

template = cv2.imread('feature_matching/feature_speaker.jpg',0)
w,h = template.shape[::-1]

res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where(res>=threshold)

for pt in zip(*loc[::-1]):
    cv2.rectangle(img_bgr, pt, (pt[0]+w, pt[1]+h), (0,255,255), 1)

cv2.imshow('template', template)
cv2.imshow('detected', img_bgr)
cv2.waitKey(0)