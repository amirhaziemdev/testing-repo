'''
Created on 7 Jan 2019

@author: Amir Haziem Razali

Code for inspection of car doors. Fine threholding is needed for this one, might also need a higher res
camera for proper detection of all features of car door. Simple masking should be sufficient
for a "template" inspection i.e. overlaying the thresholded mask (or outline) and accounting for
rotations/translations IRL but only STRICTLY for this application

This version uses Canny Edge detection, not sure how this will turn out but it seems that from test images,
the program cannot possibly identify the smaller, more intricate parts of the image. This may call for higher
resolution of camera. (Hardware restraint)
'''

import cv2
from matplotlib import pyplot as plt

v_thresh = 255 #play around with this value

def main():
    img = cv2.imread('cardoor_test_photos/cardoor-07-01-2019-14-29-21.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     img = cv2.GaussianBlur(img, (1,1), 0)
    ret,th1 = cv2.threshold(img,v_thresh,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    edges = cv2.Canny(img, 100, 200)
    
    if ret:
#         cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
#         cv2.imshow("Image", th1)
        plt.subplot(121), plt.imshow(th1, cmap = 'gray')
        plt.title('Thresh Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(edges, cmap = 'gray')
        plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
        
        plt.show()
    cv2.waitKey(0)
    
    return 0


def detect_features(img):
    image = img
    
    
    return image


if __name__ == "__main__":
    main()