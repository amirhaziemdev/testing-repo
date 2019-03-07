'''
Created on 4 Mar 2019

@author: Somebody on the internet lmao
'''


import cv2
import numpy as np

camera=1
cap = cv2.VideoCapture(camera)

key = cv2.waitKey(0)&0xFF

def main():
    img = cv2.imread('feature_matching/Test_Screenshot_1.jpg')
    cv2.namedWindow('img with roi drawn')
    while True:
        ret, img = cap.read()
        if ret:
#             gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             ret, thresh = cv2.threshold(gray_image, 50, 255, cv2.THRESH_BINARY)
#             blur  = cv2.medianBlur(thresh, 7)
#         
#             img2, contours, hierarchy = cv2.findContours(~blur, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         cv2.imshow('original img', img)
#         cv2.imshow('thresh', thresh)
#         cv2.imshow('blur', blur)
        
#             cv2.drawContours(img, contours, -1, (255,255,0), 1)
            cv2.imshow('img with roi drawn', img)
            if key == ord('q'):
                break
    
    cap.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__=="__main__":
    main()
