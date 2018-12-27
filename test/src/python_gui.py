'''
Created on 26 Dec 2018

@author: USER
'''

import tkinter
import cv2
import PIL.Image, PIL.ImageTk

camera = 0
cap = cv2.VideoCapture(int(camera))

class App:
    def __init__(self, window, window_title, image_path = 'Screenshot_26122018151851.jpg'):
        self.window = window
        self.window.title(window_title)
        
        #load an image using opencv
        while(True):
            ret, frame = cap.read()
            self.cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            #get the image dimensionas (opencv stores image data as numpy array)
            self.height, self.width, no_channels = self.cv_img.shape
            
            #create a canvas that can fit the above image
            self.canvas = tkinter.Canvas(window, width = self.width, height = self.height)
            self.canvas.pack()
            
            #use PIL to convert numpy array to a photoimage
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
            
            #add a photoimage to the canvas
            
            self.canvas.create_image(0,0,image = self.photo, anchor = tkinter.NW)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        
        #Button that lets the user blur the image
        self.btn_blur = tkinter.Button(window, text='Blur', width = 50, command = self.blur_image)
        self.btn_blur.pack(anchor=tkinter.CENTER, expand = True)
        
        
        
        self.window.mainloop()
        
        #callback for BLUR button
    def blur_image(self):
        self.cv_img = cv2.blur(self.cv_img, (3,3))
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.cv_img))
        self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

def main():
    
    App(tkinter.Tk(), "Tkinter and OpenCV")
    
    return 0;

if __name__ == "__main__":
    main()
