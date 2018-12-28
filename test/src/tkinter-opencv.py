'''
Created on 28 Dec 2018

@author: Solarian Programmer, Amir Haziem Razali
@source: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/

Base code for GUI and openCV display obtained from @source.
I added additional GUI functionalities and will add image processing code
and threshold adjustment code later.
'''
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time

cam = 0

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
        
        #sliders/spinboxes for controlling threshold
        self.sliders_px_hi = tkinter.Spinbox(window, from_=0, to=50, command = self.set_thresh)
        self.sliders_px_hi.pack(anchor = tkinter.E)
        self.sliders_px_lo = tkinter.Spinbox(window, from_=0, to=50, command = self.set_thresh)
        self.sliders_px_lo.pack(anchor = tkinter.E)
        
        #after it is called once, the update will be automatically called after every delay ms
        self.delay = 15
        self.update()
        
        self.window.mainloop()
    
    def set_thresh(self):
        self.thresh_px_hi = self.sliders_px_hi.get()
        print("current hi thresh value: ",self.thresh_px_hi)
        self.thresh_px_lo = self.sliders_px_lo.get()
        print("current hi thresh value: ",self.thresh_px_lo)
        
    def snapshot(self):
        #get a frame from video source
        ret, frame = self.vid.get_frame()
        
        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    def update(self):
        #get a frame from video source
        ret,frame = self.vid.get_frame()
        
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
        
        #key stop does not work!!! might have to find another place to put this
        #or specify another method::: google bind in class or some shit
        if cv2.waitKey(0) & 0xFF == ord('q'):
            self.quit
            self.vid.release()
            cv2.destroyAllWindows()
            
        self.window.after(self.delay, self.update)
        


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
    
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            
            
def main():
    App(tkinter.Tk(), "tkinter and opencv")
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    