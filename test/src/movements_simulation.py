'''
Created on 18 Jan 2019

@author: Amir Haziem Razali

Code for updating mechanism. At the moment, it's just showing random movements of the robot but with the help of Dijkstra or other
path-planning algorithms, this can be used to display such movements/path plan for the robots.
Class definition was initially called "Robot" but it was switched to "Simulation" for this application.
Robot instantiation will occur multiple times depending on the number of AGV robots available for use within the factory/warehouse
so further implementation of this code should leave room or account for communications between the robots.
Should also account for obstacles that are set based on the factory layout.
Can also implement YOLO code or any other human or object detection algorithms to prevent robot(s) from colliding with humans.
'''

import tkinter
import numpy as np
import cv2
import random as rd
import PIL.Image, PIL.ImageTk

#creates a black 512x512 image, three channels to suit the RGB format in cv2
img = np.zeros((512,512,3), np.uint8)

class Simulation():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.delay = 50 #ms
        
        self.width = 512
        self.height = 512
        
        self.current = [int(self.width/2),int(self.height/2)] #starting point is at 50,50
        self.frame = img
        
        #create canvas
        self.canvas = tkinter.Canvas(window, width = self.width, height = self.height)
        self.canvas.pack()
        
        self.update()
        
        self.window.mainloop()
    
    def draw_lines(self):
        [nextX, nextY] = self.random_movements()
        temp = [self.current[0]+nextX, self.current[1]+nextY]
        cv2.line(self.frame,(self.current[0],self.current[1]),(temp[0],temp[1]), (255,0,0))
        self.current = temp
    
    def random_movements(self):
        '''
        outputs random coordinates for movements
        '''
        x = rd.randint(-1,1)
        y = rd.randint(-1,1)
        
        return x,y
        
    def update(self):
        '''
        calls update after a delay
        '''
        self.draw_lines()
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
        self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
        print(self.current)
        self.window.after(self.delay, self.update)
        
def main():
    window = tkinter.Tk()
    Simulation(window, "Simulation")
    
    return 0

if __name__ == "__main__":
    main()