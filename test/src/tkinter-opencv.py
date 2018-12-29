'''
Created on 28 Dec 2018

@author: Solarian Programmer, Amir Haziem Razali
@source: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/

Base code for GUI and openCV display obtained from @source.
I added additional GUI functionalities and will add image processing code
and threshold adjustment code later.

Version 29/12/18
Added image processing capabilities and overlay/darkbg options.
Added extra GUI for controlling overlay/darkbg
Fixed bug with command functions in overlay/darkbg buttons (bracket at function call was the culprit)
Fixed bug with setting/getting overlay/darkbg functions.

Note to self:
Add options to adjust camera specs. Resolutions, distances, angle, field of view, etc.
For manual adjustments (29/12/18)


'''
import numpy as np
from imutils import contours
from skimage import measure 
import imutils
import datetime
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
from Tools.scripts.texi2html import increment
from tkinter import StringVar

#default values, can be included in GUI
cam = 0
d = 15 #cm
de = 40 #cm
f = 0.375 #factor by which the distance is multiplied

class App():
    def __init__(self, window, window_title, video_source=cam):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        
        #open video source
        self.vid = MyVideoCapture(self.video_source)
        
        #create a canvas with given dimensions
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()
        
        #button for taking screenshots
        self.btn_snapshot = tkinter.Button(window, text = "Snapshot", width = 50, command = self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand = True)
        
        #initialise values
        [self.thresh_px_lo, self.thresh_px_hi, self.thresh_rd_lo, self.thresh_rd_hi] = [1, 20000, 12, 1000]
        var1 = StringVar(window)
        var2 = StringVar(window)
        var3 = StringVar(window)
        var4 = StringVar(window)
        var1.set("20000")
        var2.set("1")
        var3.set("1000")
        var4.set("12")
        self.darkbg = False
        self.overlay = True
        
        #sliders/spinboxes for controlling threshold
        self.sliders_px_hi = tkinter.Spinbox(window, from_=0, to=20000, command = self.set_thresh, increment = 100.0, textvariable = var1)
        self.sliders_px_hi.pack(anchor = tkinter.E)
        self.sliders_px_lo = tkinter.Spinbox(window, from_=0, to=100, command = self.set_thresh, textvariable = var2)
        self.sliders_px_lo.pack(anchor = tkinter.E)
        self.sliders_rd_hi = tkinter.Spinbox(window, from_=0, to=10000, command = self.set_thresh, increment = 100.0, textvariable = var3)
        self.sliders_rd_hi.pack(anchor = tkinter.E)
        self.sliders_rd_lo = tkinter.Spinbox(window, from_=0, to=100, command = self.set_thresh, textvariable = var4)
        self.sliders_rd_lo.pack(anchor = tkinter.E)
        
        #buttons for controlling overlay, darkbg
        self.btn_darkbg = tkinter.Button(window, text = "Dark Background", width = 20, command = self.set_darkbg)
        self.btn_darkbg.pack(side = 'left')
        self.btn_overlay = tkinter.Button(window, text = "Overlay", width = 20, command = self.set_overlay)
        self.btn_overlay.pack(side = 'left')
#         self.btn_snapshot = tkinter.Button(window, text = "Snapshot", width = 50, command = self.snapshot)
#         self.btn_snapshot.pack(anchor=tkinter.CENTER, expand = True)
        
        #after it is called once, the update will be automatically called after every delay ms
        self.delay = 15
        self.update()
        
        self.window.mainloop()
    
    #boolean, will return true or false
    def set_darkbg(self):
        if self.darkbg == True:
            self.darkbg = False
        elif self.darkbg == False:
            self.darkbg = True
        print('darkbg: ', self.darkbg)
        
    def get_darkbg(self):
        return self.darkbg
    
    def set_overlay(self):
        if self.overlay == True:
            self.overlay = False
        elif self.overlay == False:
            self.overlay = True
        print('overlay: ', self.overlay)
        
    def get_overlay(self):
        return self.overlay
    
    def set_thresh(self):
        self.thresh_px_hi = self.sliders_px_hi.get()
        print("current hi thresh px value: ",self.thresh_px_hi)
        self.thresh_px_lo = self.sliders_px_lo.get()
        print("current low thresh px value: ",self.thresh_px_lo)
        self.thresh_rd_hi = self.sliders_rd_hi.get()
        print("current hi thresh rd value: ",self.thresh_rd_hi)
        self.thresh_rd_lo = self.sliders_rd_lo.get()
        print("current low thresh rd value: ",self.thresh_rd_lo)
        
    def get_thresh(self):
        return [int(self.thresh_px_lo), int(self.thresh_px_hi), int(self.thresh_rd_lo), int(self.thresh_rd_hi)]
        
    def snapshot(self):
        #get a frame from video source
        ret, frame = self.vid.get_frame()
        
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    def update(self):
        #get a frame from video source
        ret,frame = self.vid.get_frame()
        
        if ret:
            frame = self.mould_detection(frame)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
        
        #key stop does not work!!! might have to find another place to put this
        #or specify another method::: google bind in class or some shit
        if cv2.waitKey(0) & 0xFF == ord('q'):
            self.quit
            self.vid.release()
            cv2.destroyAllWindows()
            
        self.window.after(self.delay, self.update)
    
    def mould_detection(self,frame):
        image = frame
        self.feed = frame
        [pxthresh_low, pxthresh_high, r_low, r_high] = self.get_thresh()
        darkbg =  self.get_darkbg()
        overlay = self.get_overlay()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        if darkbg:
            thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
        else:
            thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
        
        labels = measure.label(thresh, neighbors=8, background=0)
        blur = cv2.GaussianBlur(gray,(5,5),0)
        ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        thresh = th3
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
            
            if numPixels > pxthresh_low and numPixels < pxthresh_high:
                mask = cv2.add(mask, labelMask)
                
        
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        try:
            cnts = contours.sort_contours(cnts)[0]
        except:
            print("No holes detected!")
        #loop over contours
        for i, c in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            
    #         if radius > r_high or radius < r_low:
    #             cnts[i] = 0
            if radius < r_high and radius > r_low:
                if overlay:
                    cv2.circle(image, (int(cX), int(cY)), int(radius), (0,0,255), 3)
                    print("circle no. {}".format(i+1), "radius:", radius, "center:", cX, ",", cY)
                    cv2.putText(image, "hole # {}".format(i+1), (x,y -15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 2)
                    cv2.rectangle(image, (int(cX-(w/2)), int(cY-(h/2))), (int(cX+(w/2)), int(cY+(h/2))), (255,0,0), 2)
            
                if cX > 320:
                    coordX = (cX - 320)/d
                else:
                    coordX = -(320 - cX)/d
            
                coordY = (460 - cY)/d
                [coordX, coordY] = [round(coordX, 2), round(coordY, 2)]
                #converting h,w to real sizes from pixel size
                [h,w] = [round(h/d, 2), round(w/d, 2)]
                area = round(h*w, 2)
                if overlay:
                    cv2.putText(image, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    cv2.putText(image, "height and width: ({},{})".format(h, w), (int(cX - radius),int(cY +radius) + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    cv2.putText(image, "area: ({})".format(area), (int(cX - radius),int(cY +radius) + 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    cv2.line(image, (0, 460), (640, 460), color = 255)
                    cv2.line(image, (320, 0), (320, 480), color = 255)
                    cv2.circle(image, (320, 460), 5, (255, 0, 0), 1)
                    self.feed = image
                else:
#                     cv2.putText(thresh, "coords: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
#                     cv2.line(thresh, (0, 460), (640, 460), color = 255)
#                     cv2.line(thresh, (320, 0), (320, 480), color = 255)
#                     cv2.circle(thresh, (320, 460), 5, (255, 0, 0), 1)
                    self.feed = image
    
        
        return self.feed


class MyVideoCapture():
    def __init__(self, video_source = cam):
        #open video source
        self.vid = cv2.VideoCapture(video_source)
        
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source: ", video_source)
        
        #get video source height and width
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                #return a boolean success flag and the current frame in BGR format
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
    
    #in the event of delete window
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            
            
def main():
    App(tkinter.Tk(), "tkinter and opencv")
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    