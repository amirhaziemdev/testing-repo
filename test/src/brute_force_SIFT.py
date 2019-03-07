'''
Created on 14 Feb 2019
Happy Valentine's Day!
@author: Amir Haziem Razali
trying out brute force matching with SIFT, let's hope this works

Error log shows:
Traceback (most recent call last):
  File "C:\\Users\\USER\git\repository\test\src\brute_force_SIFT.py", line 23, in <module>
    sift = cv2.xfeatures2d.SIFT_create()
cv2.error: OpenCV(3.4.5) C:\projects\opencv-python\opencv_contrib\modules\xfeatures2d\src\sift.cpp:1207: error: (-213:The function/feature is not implemented) This algorithm is patented and is excluded in this configuration; Set OPENCV_ENABLE_NONFREE CMake option and rebuild the library in function 'cv::xfeatures2d::SIFT::create'
'''

import numpy as np
import cv2

from matplotlib import pyplot as plt

img1 = cv2.imread('feature_matching/feature_handle.jpg',0)
img2 = cv2.imread('feature_matching/Test_Screenshot_3.jpg',0)

#init SIFT detector
sift = cv2.xfeatures2d.SIFT_create()

kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

#apply ratio test
good = []
for m,n in matches:
    if m.distance < 0.75*n.distance:
        good.append([m])

img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,flags=2)

plt.imshow(img3),plt.show()