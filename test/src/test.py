'''
Created on 17 Dec 2018

@author: USER
'''
import numpy
import cv2

cap = cv2.VideoCapture(0)

# this is a test

def main():
    
    print("Hewwo World!\n")
    print('running test diagnostics...\n')
    print('initialising simple calculations\n')
    
    add_value = calc_add(2, 3)
    
    print("adding two numbers...\nresult:", add_value)
    
    print('testing display function...')
    
    display_cam()
    print('test is done! python running smoothly')
    return 0

def calc_add(a, b):
    
    return a+b
    
def display_cam():
    
    while(True):
        # capture frame by frame
        ret, frame = cap.read()
        
        #operations on frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #display resulting frame
        cv2.imshow('Webcam Feed', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    #release the capture
    cap.release()
    cv2.destroyAllWindows()
    
    
if __name__ == "__main__":
    main()