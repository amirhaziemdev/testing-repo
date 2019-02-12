'''
Created on 12 Feb 2019

@author: Amir Haziem Razali
GUI for demo in Germany
'''

import tkinter
from tkinter.scrolledtext import ScrolledText
from tkinter import Button
from tkinter import LabelFrame
import cv2


class Inspection():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        
        self.btn_setfeature = Button(self.window, height=2, width=8, text='Set Feature', command = self.printStatus)
        self.btn_setfeature.grid(column=3, row=6, rowspan=2)
        self.btn_clrfeature = Button(self.window, height=2, width=8, text='Clear Feature', command = self.clearStatus)
        self.btn_clrfeature.grid(column=5, row=6, rowspan=2)
        
        self.textboxFrame = LabelFrame(self.window)
        self.textboxFrame.grid(row=6, column=1, rowspan=2)
        self.statusBox = ScrolledText(self.textboxFrame, height=5, width=40, bg = 'white')
        self.statusBox.grid(row=6, column=1, rowspan=2)
        
        self.delay = 50
        self.counter = 0
        self.newText = 'Germany module'
        self.update()
        
        self.window.mainloop()
        
    def clearStatus(self):
        self.counter = 0
        self.statusBox.insert('1.0', 'Counter cleared!\n')
        print('Counter cleared!')
    
    def printStatus(self):
        self.counter += 1
        self.statusBox.insert('1.0', self.newText+' Times button pressed: '+str(self.counter)+'\n')
        print(self.newText, 'Times button pressed:',self.counter)
    
    def update(self):
        self.window.after(self.delay, self.update)

def main():
    
    Inspection(tkinter.Tk(), "Germany DEMO")
#     Inspection(tkinter.Tk(), "Germany DEMO 2")
    
    return 0


if __name__=="__main__":
    main()
