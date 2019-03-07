'''
Created on 29 Jan 2019

@author: Amir Haziem Razali
Base code for fleet management system. Should consist of two classes for 1) fleet management GUI and 2) creation of AGV object
'''

import tkinter
from tkinter.scrolledtext import ScrolledText
import random as rd
import cv2

class GUI():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        self.canvas = tkinter.Canvas(self.window, width=50)
        self.connections = []
        for i in range(8):
            self.connections.append([i, 'COM'+str(rd.randint(2,16))])
        print(self.connections)
        self.AGV = []
#         self.AGV = self.create_AGV()
        
        self.amount_AGV = tkinter.StringVar(value = '1')
        self.spbx_createAGV = tkinter.Spinbox(self.window, textvariable = self.amount_AGV)
        self.spbx_createAGV.grid(column=1, row=1)
        self.btn_createAGV = tkinter.Button(self.window, text="Create AGV", command=self.create_AGV)
        self.btn_createAGV.grid(column=2, row=1)
        
        self.textframe = tkinter.LabelFrame(self.window, width=50)
        self.textframe.grid(row=1,column=0)
        self.textbox = ScrolledText(self.textframe)
        self.textbox.grid(row=1,column=0)
        
        self.window.mainloop()
    
    def create_AGV(self):
        '''
        check for number of connections (IP, etc.) and create AGV objects based on the number of connections
        should only be called once.
        '''
        for i,j in enumerate(self.connections):
            temp = AGV(ID=i,connection_status=j[1])
            self.textbox.insert('1.0','AGV {} created using port {}\n'.format(temp.ID, temp.connection))
            self.AGV.append(temp)

class AGV():
    def __init__(self, ID, connection_status):
        self.ID = ID
        self.connection = connection_status
        
    def obstacle_detection(self, coords, size):
        '''
        obstacles should arrive in the assumed form of a rectangle where:
        1) the variable coords stores the x,y coordinates of the first point of contact of obstacles (one corner), and
        2) the variable size stores the width and height (in planar view) of the obstacle(s)
        so,
        coords = [x,y]; size = [w,h]
        '''
        [x,y] = [coords[0], coords[1]]
        [w,h] = [size[0], size[1]]
    


def main():
    tk = tkinter.Tk() #will be passed into GUI object
    GUI(tk,'CMS GUI')
    
    return 0

if __name__=="__main__":
    main()