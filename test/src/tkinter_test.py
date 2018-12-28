'''
Created on 28 Dec 2018

@author: USER
'''
from tkinter import *
import numpy as np
import cv2

cap = cv2.VideoCapture(0)

class Application(Frame):
    def say_hi(self):
        print("hi there, everyone!")
        
    def adjust_thresh(self):
        self.my_thresh = self.thresh.get()
        print("current thresh value:", self.my_thresh)
        
    def set_thresh(self):
        self.current_thresh = self.thresh.get()
        self.adjust_thresh()
        return self.current_thresh
    
    def get_thresh(self):
        return self.current_thresh
    
    def show_feed(self):
        return 0
        

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})
        
        self.showfeed = Button(self)
        self.showfeed["text"] = "Show Feed",
        self.showfeed["command"] = self.show_feed
 
        self.showfeed.pack({"side": "right"})
        
        self.thresh = Spinbox(self, from_=0, to=10)
        self.thresh["text"] = "Threshold"
        self.thresh["command"] = self.set_thresh
        
        self.thresh.pack({"side":"right"})
        
        
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.current_thresh = 0
        self.camera_feed = cap
        self.show_feed()
        ret, frame = cap.read()
        cv2.imshow("Feed",frame)
        self.pack()
        self.createWidgets()

def main():
    root = Tk()
    app = Application(master=root)
#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break
    app.mainloop()
    root.destroy()
    cap.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == "__main__":
    main()


