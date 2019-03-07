'''
Created on 12 Feb 2019

@author: Amir Haziem Razali
Code for experimenting with feature extraction and feature matching

'''


import cv2
import numpy as np

cv2.namedWindow('matching results')
feature_dir = 'feature_matching/feature_wholedoor'
feature_dir = feature_dir + '.jpg'
photo_dir = 'feature_matching/Test_Screenshot_1'
photo_dir = photo_dir + '.jpg'

thresh=30
camera = 0
key = 0xFF & cv2.waitKey(0)

def main():
    img1 = cv2.imread(feature_dir, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(photo_dir, cv2.IMREAD_GRAYSCALE)
    
#     cap = cv2.VideoCapture(camera)
    
    #using ORB
    orb = cv2.ORB_create()
    
#     while True:
#         ret,frame = cap.read()
#         if ret:
#             img3 = frame
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    #brute force matching
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
#     matches = bf.knnMatch(np.asarray(des1, np.uint8), np.asarray(des2,np.uint8), k=1)
    matches = sorted(matches, key=lambda x:x.distance)
    
    print(len(matches))
    
    if thresh!=0:
        matching_results = cv2.drawMatches(img1, kp1, img2, kp2, matches[:thresh], None, flags=2)
    else:
        matching_results = cv2.drawMatches(img1, kp1, img2, kp2, matches[:], None, flags=2)
        
    for m in matches:
        print(m.distance)
#         
#         cv2.imshow('feature', img1)
#         cv2.imshow('photo', img2)
    cv2.imshow('matching results', matching_results)
#     if key == ord('q'):
#         break

#     cap.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
if __name__=="__main__":
    main()