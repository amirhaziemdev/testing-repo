'''
Created on 12 Feb 2019

@author: Amir Haziem Razali
GUI for demo in Germany

Version 23/2/2019
GUI construction OK, needs more development
- Needs feature matching code included. 
- Needs status boxes for OK/NO-GO
'''

import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import Button
from tkinter import LabelFrame
import numpy as np
import cv2
import PIL.Image, PIL.ImageTk

cam = 0
camera = 0


class Inspection():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = camera
        
        self.btn_setfeature = Button(self.window, height=2, width=8, text='Set Feature', command = self.printStatus)
        self.btn_setfeature.grid(column=3, row=6, rowspan=2)
        self.btn_clrfeature = Button(self.window, height=2, width=8, text='Clear Feature', command = self.clearStatus)
        self.btn_clrfeature.grid(column=5, row=6, rowspan=2)
        
        self.dummy = True
        self.btn_dummy = Button(self.window, height=2, width=8, text="Dummy", command = self.setDummy)
        self.btn_dummy.grid(column=7, row = 6, rowspan=2)
        
        self.vid = MyVideoCapture(self.video_source)
        
        self.canvas = tkinter.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas.grid(row=0, column=0, columnspan=3)
        
        self.statusCanvas = tkinter.Canvas(self.window, width=self.vid.width/2, height = self.vid.height/2, bg='cyan')
        self.statusCanvas.grid(row=0, column=3, columnspan=5)
        
        txlogo = cv2.imread('txmr.jpg') #reads correctly, checked with imshow
#         txlogo_small = cv2.resize(txlogo, (0,0), fx=0.25, fy=0.25)
        
        self.txcanvas = tkinter.Canvas(self.window)
        self.txcanvas.grid(row=0, column=3, columnspan=3)
        
        self.txphoto = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(txlogo))
        self.txcanvas.create_image(0,0, image = self.txphoto)
        
        self.textboxFrame = LabelFrame(self.window)
        self.textboxFrame.grid(row=6, column=1, rowspan=2)
        self.statusBox = ScrolledText(self.textboxFrame, height=10, width=78, bg = 'white')
        self.statusBox.grid(row=6, column=1, rowspan=2)
        
        self.delay = 50
        self.counter = 0
        self.newText = 'Germany module'
        self.update()
        
        self.window.mainloop()
    
    def setDummy(self):
        if self.dummy == True:
            self.dummy = False
        else:
            self.dummy = True
        self.statusBox.insert('1.0', 'Dummy:'+str(self.dummy)+'\n')
        print("Dummy:",self.dummy)
        
    def clearStatus(self):
        self.counter = 0
        self.statusBox.insert('1.0', 'Counter cleared!\n')
        print('Counter cleared!')
    
    def printStatus(self):
        self.counter += 1
        self.statusBox.insert('1.0', self.newText+' Times button pressed: '+str(self.counter)+'\n')
        print(self.newText, 'Times button pressed:',self.counter)
    
    def update(self):
        ret,frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.update)

class MyVideoCapture():
    def __init__(self, video_source):
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
    
    Inspection(tkinter.Tk(), "Germany DEMO")
    
    return 0


if __name__=="__main__":
    main()
