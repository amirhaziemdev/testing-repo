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

#step size
step = 50
offset = 5

#creates a black 512x512 image, three channels to suit the RGB format in cv2
img = np.zeros((512,512,3), np.uint8)

#keywait
key = cv2.waitKey(0) & 0xFF
#obstacles, [x1,y1,x2,y2]
obstacles = [[10,100,100,150],
             [300,400,450,450]]
walls = [0,0,512,512]

class Simulation():
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.delay = 100 #ms
        
        self.width = 512
        self.height = 512
        
        self.current = [int(self.width/2),int(self.height/2)] #starting point is at 50,50
        self.frame = img
        self.obstacles = obstacles
        #create canvas
        self.canvas = tkinter.Canvas(window, width = self.width, height = self.height)
        self.canvas.pack()
        
        self.update()
        
        self.window.mainloop()
    
    def draw_obstacles(self):
        for i,j in enumerate(self.obstacles):
            cv2.rectangle(self.frame, (j[0],j[1]), (j[2],j[3]), (255,0,255), 2)
        #draw walls
        cv2.rectangle(self.frame, (walls[0], walls[1]), (walls[2], walls[3]), (0,0,255), 3)
    
    def draw_lines(self):
        [nextX, nextY] = self.random_movements()
        curr = self.current
        next = [self.current[0]+nextX, self.current[1]+nextY]
        for i, j in enumerate(obstacles): #if
#             next = [self.current[0]+nextX, self.current[1]+nextY]
            #check if it is within the walls first
            if next[0] in range(walls[0]+offset,walls[2]-offset) and next[1] in range(walls[1]+offset,walls[3]-offset):
                if (next[0] in range(j[0],j[2])) and (next[1] in range(j[1],j[3])) and (curr[0] in range(j[0],j[2])) and (curr[1] in range(j[1],j[3])):
                    print('condition failed, waiting for new coordinates. current:({},{})'.format(curr[0], curr[1]))
                    print('condition failed, waiting for new coordinates. next:({},{})'.format(next[0], next[1]))
                    self.current = curr
                else:
                    cv2.line(self.frame,(curr[0],curr[1]),(next[0],next[1]), (255,0,0), lineType = cv2.LINE_AA)
                    print('iteration {} successful. obstacle {} avoided'.format(i+1,i+1))
                    self.current = next

    
    def random_movements(self):
        '''
        outputs random coordinates for movements
        '''
        x = rd.randint(-step, step)
        y = rd.randint(-step, step)
        
        return x,y
        
    def update(self):
        '''
        calls update after a delay
        '''
        self.draw_lines()
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
        self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
        print(self.current)
        self.draw_obstacles()
        #doesn't work...
        if key == ord('q'):
            self.destroy()
        
        self.window.after(self.delay, self.update)
    
    def destroy(self):
        print('destroying...')
        self.window.destroy()
        
def main():
    window = tkinter.Tk()
    Simulation(window, "Simulation")
    
    return 0

if __name__ == "__main__":
    main()