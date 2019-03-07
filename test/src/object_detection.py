'''
Created on 2 Jan 2019

@author: Adrian Rosebrock & Amir Haziem Razali
@source: https://www.pyimagesearch.com/2018/07/30/opencv-object-tracking/

base code lifted from @source written by Adrian Rosebrock
Added on by Amir Haziem Razali
'''

from imutils.video import VideoStream
from imutils.video import fps
import argparse
import imutils
import time
import cv2
from imutils.video.fps import FPS

#construct argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default='kcf', help="OpenCV object tracker type, defaulted to KCF")
args = vars(ap.parse_args())

#extract OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

#prior to openCV 3.2, can use a special factory function to create the object tracker
if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())
else:
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }

#init bounding box coords of the object we are going to track
initBB = None

#if a video path was not supplied, grab the reference to the webcam (or in this case, videocam)
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    #otherwise, grab a ref to the vid file
    vs = cv2.VideoCapture(args["video"])


#grab appropriate object tracker using dictionary of opencv object trackers
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()
    
#init FPS throughput estimator
fps = None

#loop over frames
while(True):
    #grab current frame, then handle if we're using a videostream of videocapture object
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    
    #check to see if we've reached the end of the stream
    if frame is None:
        break
    
    #resize the frame (so we can process it faster) and grab the frame dimensions
    frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]
    
    #check to see if we're currently tracking an object
    if initBB is not None:
        #grab the new bounding box coords of the object
        (success, box) = tracker.update(frame)
        
        #check to see if the tracking was a success
        if success:
            (x,y,w,h) = [int(v) for v in box]
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
            
        #update the FPS counter
        fps.update()
        fps.stop()
        
        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps()))
        ]
        
        #loop over the info tuples and draw them on our frame
        for (i, (k,v)) in enumerate(info):
            text = "{}: {}".format(k,v)
            cv2.putText(frame, text, (10, H - ((i*20)+20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                         
    #show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
            
        #if the 's' key is selected, we are going to select a boundary box to track
    if key == ord("s"):
        #select the bounding box of the object that we want to track
        #make sure you press ENTER or SPACE after selecting ROI
        initBB = cv2.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)
                
        #start openCV object tracker using the supplied boundary box coordinates, then
        #start the FPS throughput estimator
        tracker.init(frame, initBB)
        fps = FPS().start()
    elif key == ord("q"):
        break
        
if not args.get("video", False):
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
            
            