'''
Created on 10 Jan 2019

@author: Amir Haziem Razali

Base code lifted from tkinter-opencv test project.
Added to repo

This is for solely controlling the conveyor safety feature at plate one of the conveyor belt
'''
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
Fixed minor alignment problems with GUI widgets

Version 3/1/2019
Added extra functions (not called) for mold ID #
Added class Mold to make Mold objects so it's OOP 

Version 4/1/2019
Added manual cam width and height constants (adjustable at source). In the future this can be fetched from the actual camera data.
Maybe add a GUI setting functionality for this OR do an INIT .txt file to fetch camera data.

Version 14/1/2019
Some major changes:
Erased overwriting thresh frame with another thresh (th3 line commented out). Should make it adjustable in GUI or txt file (pick one) <--- this has been causing inaccuracies in detection
Implemented ROI functionalities. Might not work but we'll give it a try. <---- first implementation
Implemented zero-indexing for mold identifiers
Implemented y_thresh for focusing on "higher than y_thresh pixel coordinates" i.e. ONLY FOCUS ON LOWER Y PIXELS. Should change this to ratio of the resolution or something, this couldn't possibly work with different cameras

Version 15/1/2019
Added sending mechanism (only prints a string message, have yet to include serial communications)
Debugged the send_command mechanism and push button
Changed default values of visible molds (nothing major)
Still needs work: timing for update of molds, can it be something like 1.25 - 1.5 seconds or something?
To temporarily debug this, the text boxes store the '1' value indefinitely if something is detected within the boxes
Changed the default ROI center tolerance to 0.5 (50%). This needs to be adjusted

Version 16/1/2019
Added timing function for send_command function. This should delay updates by 1.5 seconds (adjustable) as required by PLC

Version 17/1/2019
Removed keystop in self.update() function, it's been causing bugs. Normal stop (X button on GUI) should suffice for this application


missing implementation for sending over serial cable.
please include (14/1/2019)
        
(24/1/2019): Adding ser.write() mechanism in App.send_command, watch out for bugs

important point: please update the status at ID in the Tkinter window with respect to its ID here.
Definition of region of interest will be crucial to this application.
Also please create text box to update the status at ROI (done 11/1/2019) - Amir

Version 4/2/2019
Removed a chunk of code and various implementations are either added or removed, I lost track of everything.
But this version should be the final webcam version before implementing IP camera in the actual conveyor.
Implemented dictionary for easy import of constants from text file. Current text file is configs.txt
This version also includes implementation for direct modbus communications, omitting the serial class implementation.

Note to self:
Add options to adjust camera specs. Resolutions, distances, angle, field of view, etc.
For manual adjustments. Fix alignments for buttons and spinboxes. Please also add text/label beside
(or inside) every spinbox/options/buttons (29/12/18)
Maybe consider a delayed update function for the status/ID textboxes? Needs a different update mechanism including careful 
placement of function calls. 


'''
import numpy as np
from imutils import contours
from skimage import measure 
import imutils
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import random as rd
import serial_rx_tx
import serial
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from pymodbus.client.sync import ModbusSerialClient

#default values, can be included in GUI
#these settings should be in an .init file or something
#should be a text file with editable constants along with the executable
directory = 'configs.txt'
my_constants = {
    "cam":'0',
    "comport":'0',
    "baud":'0',
    "send_interval":'0',
    "slave_ID":'0',
    "start_address":'0',
    "d":'0',
    "de":'0',
    "f":'0',
    "cam_width":'0',
    "cam_height":'0',
    "center_tolerance":'0',
    "y_thresh":'0',
    "v_thresh":'0',
    "paddingx":'0',
    "paddingy":'0'
    }
'''
outsourcing constant values
'''
f = open(directory,mode='r')
my_lines = f.read()
temp = my_lines.split()
for i,j in enumerate(temp):
    if temp[i]=='=':
        del(temp[i])

for x,y in my_constants.items():
    for i,j in enumerate(temp):
        if x==temp[i]:
            try:
                my_constants[temp[i]] = int(temp[i+1])
            except:
                my_constants[temp[i]] = float(temp[i+1])
    
f.close()

#configurations
cam = my_constants['cam']
comport = my_constants['comport']
baud = my_constants['baud']
send_interval = my_constants['send_interval'] #ms
slave_ID = my_constants['slave_ID']
start_address = my_constants['start_address'] #address to which the program will write
d = my_constants['d'] #cm
de = my_constants['de'] #cm
f = my_constants['f'] #factor by which the distance is multiplied

#constants
cam_width = my_constants['cam_width']
cam_height = my_constants['cam_height']
center_tolerance = my_constants['center_tolerance'] #in percentage of the height and width of the OOI/mold
y_thresh = my_constants['y_thresh'] #only focus on the lower y_thresh pixels
v_thresh = my_constants['v_thresh']

#GUI constant
#label frame paddings
paddingx = my_constants['paddingx']
paddingy = my_constants['paddingy']

#defining outer boundaries of ROI, in pixels
'''
format is: [[x,y,w,h]
                ...
            ]
where (x,y) is the upper left hand corner of the rectangle
w is the width of the rectangle,
and h is its height.
This has been hard-coded in (duh!), please make it smarter -_- 
'''
tempH = 150
tempY = 150
tempROI = []
tempROI = [[0, tempY, 100, tempH],
           [80, tempY, 80, tempH],
           [160, tempY, 70, tempH],
           [250, tempY, 80, tempH],
           [310, tempY, 70, tempH],
           [380, tempY, 70, tempH],
           [450, tempY, 80, tempH],
           [530, tempY, 100, tempH]]


class App():
    def __init__(self, window, window_title, camera, portNum, baudrate):
        #init everything
        self.window = window
        self.window.title(window_title)
        self.video_source = camera
        self.portNum = 'COM'+str(portNum)
        self.baudrate = baudrate
        
        
        #Copy object serialPort
#         self.serialPort = serialPort
        self.client = ModbusSerialClient(method='rtu', port=self.portNum, baudrate=self.baudrate, parity = 'O')
#         self.serialPort.RegisterReceiveCallback(self.onReceiveSerialData)
        
        #open video source
        self.vid = MyVideoCapture(self.video_source)
        
        #create a canvas with given dimensions
        self.canvas = tkinter.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        self.canvas.grid(row=0, column=0, columnspan=20)
        
        #button for taking screenshots
        self.btn_snapshot = tkinter.Button(self.window, text = "Snapshot", width = 20, command = self.snapshot)
        self.btn_snapshot.grid(row=1, column=3)
        
        #init empty regions of interest (ROI) list
        #if any centers of rectangles fall within any of the ROIs, they automatically become detected OOIs. (i.e. status set to '1')
        self.ROIs = []
        self.set_ROIs()
        
        #initialise values, at these values all molds can currently be seen
        [self.thresh_px_lo, self.thresh_px_hi, self.thresh_rd_lo, self.thresh_rd_hi] = [1, 20000, 22, 1000]
        var1 = StringVar(self.window)
        var2 = StringVar(self.window)
        var3 = StringVar(self.window)
        var4 = StringVar(self.window)
        
        #init with default values
        var1.set(self.thresh_px_hi)
        var2.set(self.thresh_px_lo)
        var3.set(self.thresh_rd_hi)
        var4.set(self.thresh_rd_lo)
        self.darkbg = False
        self.overlay = True
        
        #init labelframe for status/ID organiser
        labelframe = LabelFrame(self.window, text="ID/Status", width = 120)
        labelframe.grid(row=2,column=0, columnspan=20)

        #init statlist
        self.statlist = []
        self.status = [0,0,0,0,0,0,0,0]
        
        #init 8 StringVar variables
        for i in range(8):
            self.statlist.append(StringVar(value = '0'))
        
        self.stat0 = Label(labelframe, textvariable=self.statlist[0], bg = 'white').grid(row = 3,column = 2, padx=paddingx, pady = paddingy)
        self.stat1 = Label(labelframe, textvariable=self.statlist[1], bg = 'white').grid(row = 3,column = 4, padx=paddingx, pady = paddingy)
        self.stat2 = Label(labelframe, textvariable=self.statlist[2], bg = 'white').grid(row = 3,column = 6, padx=paddingx, pady = paddingy)
        self.stat3 = Label(labelframe, textvariable=self.statlist[3], bg = 'white').grid(row = 3,column = 8, padx=paddingx, pady = paddingy)
        self.stat4 = Label(labelframe, textvariable=self.statlist[4], bg = 'white').grid(row = 3,column = 10, padx=paddingx, pady = paddingy)
        self.stat5 = Label(labelframe, textvariable=self.statlist[5], bg = 'white').grid(row = 3,column = 12, padx=paddingx, pady = paddingy)
        self.stat6 = Label(labelframe, textvariable=self.statlist[6], bg = 'white').grid(row = 3,column = 14, padx=paddingx, pady = paddingy)
        self.stat7 = Label(labelframe, textvariable=self.statlist[7], bg = 'white').grid(row = 3,column = 16, padx=paddingx, pady = paddingy)
#         
#         for i in range(8):
#             Label(labelframe, textvariable = self.statlist[i], bg = 'white').grid(row = 3, column = (i*2)+2, padx = paddingx, pady = paddingy)
#         
        #init Entry boxes here for focal point and distance of installment
        #this can maybe be compacted into a .txt file or something. too many options in GUI is NOT GOOD and NOT INTUITIVE
        varfocalpoint = StringVar(self.window)
        varfocalpoint.set('100')
        vardistance = StringVar(self.window)
        vardistance.set('100')
#         self.entry_focal_point = Entry(window, textvariable = varfocalpoint).pack(side=LEFT)
#         self.entry_vardistance = Entry(window, textvariable = vardistance).pack(side=LEFT)

        self.textframe = tkinter.Frame(self.window, bg='white').grid(row=5,column=1,rowspan=8,columnspan=6)
        self.textbox = ScrolledText(self.textframe, wrap='word',height=3, width=70)
        self.textbox.grid(row=5,column=1,rowspan=8,columnspan=6, pady=paddingy)
        
        #sliders/spinboxes for controlling threshold
        self.sliders_px_hi = tkinter.Spinbox(self.window, from_=0, to=20000, command = self.set_thresh, increment = 100.0, textvariable = var1)
        self.sliders_px_hi.grid(row = 7, column = 8)
        self.sliders_px_lo = tkinter.Spinbox(self.window, from_=0, to=100, command = self.set_thresh, textvariable = var2)
        self.sliders_px_lo.grid(row = 8, column = 8)
        self.sliders_rd_hi = tkinter.Spinbox(self.window, from_=0, to=10000, command = self.set_thresh, increment = 100.0, textvariable = var3)
        self.sliders_rd_hi.grid(row = 9, column = 8)
        self.sliders_rd_lo = tkinter.Spinbox(self.window, from_=0, to=100, command = self.set_thresh, textvariable = var4)
        self.sliders_rd_lo.grid(row = 10, column = 8)
        
        self.COMPortButton = StringVar(value='Open Port')
        #buttons for controlling overlay, darkbg
        self.btn_darkbg = Button(self.window, text = "Dark Background", width = 20, command = self.set_darkbg).grid(row = 12, column = 1)
        self.btn_overlay = Button(self.window, text = "Overlay", width = 20, command = self.set_overlay).grid(row = 12, column = 2)
        self.dummy = Button(self.window, text = 'Dummy Press', width = 20, command = self.dummy_button_press).grid(row = 12, column = 3)
        self.btn_porttoggle = Button(self.window, textvariable = self.COMPortButton, width = 20, command = self.portToggle).grid(row = 12, column = 4)

        self.temp = 0
        #after it is called once, the update will be automatically called after every delay ms
        self.delay = 15
        self.senddelay = send_interval
#         self.send_IO()
        self.update()
        
        self.window.mainloop()
        
    def send_IO(self):
        for i,j in enumerate(self.statlist):
            if self.statlist[i].get() == '1':
                self.client.write_coil(start_address+i, value=1, unit=slave_ID)
                print('Writing 1 to address:', start_address+i)
            elif self.statlist[i].get() == '0':
                self.client.write_coil(start_address+i, value=0, unit=slave_ID)
                print('Writing 0 to address:', start_address+i)
            self.statlist[i].set('0')
        self.window.after(self.senddelay, self.send_IO)
        
    def portToggle(self):
        if self.COMPortButton.get() == 'Open Port':
            self.send_IO()
            self.COMPortButton.set('Close Port')
        else:
            self.COMPortButton.set('Open Port')
    
    def openPort(self):
        try:
            self.serialPort.Open(self.portNum,self.baudrate)
            self.textbox.insert('1.0','COM Port {} opened!\n'.format(self.portNum))
            self.COMPortButton.set('Close Port')
            self.send_command() #start sending commands
        except:
#             self.textbox.insert('1.0','COM Port {} open failed.\n'.format(self.portNum))
            print('COM Port {} open unsuccessful'.format(self.portNum))
        print('COM Port {} opened!'.format(self.portNum))
    
    def closePort(self):
        if self.serialPort.IsOpen():
            self.serialPort.Close()
            self.textbox.insert('1.0', 'COM Port {} closed successfully!\n'.format(self.portNum))
            self.COMPortButton.set('Open Port')
        else:
            self.textbox.insert('1.0', 'COM Port already closed!\n')
    
    #will only be called once, ROIs are RIGID
    def set_ROIs(self):
        for i, j in enumerate(tempROI):
            self.ROIs.append(self.calculate_ROI_corners(j[0],j[1],j[2],j[3]))
        print(self.ROIs)
        
    #to be sent to filling PLC
    def convert_to_string(self):
        value = self.statlist[0].get() + self.statlist[1].get()+ self.statlist[2].get()+ self.statlist[3].get()+ self.statlist[4].get()+ self.statlist[5].get()+ self.statlist[6].get()+ self.statlist[7].get()
        value_str = value
        value = hex((int(value, base=2)))
        return value, value_str
    #detects if centers fall within the ROI and updates the current status
    def update_status(self, cX, cY):
        for i, j in enumerate(self.ROIs):
            if cX > j[0] and cX < j[2] and cY > j[1] and cY < j[3]:
                self.statlist[i].set('1')
            elif self.statlist[i].get()!='1':
                self.statlist[i].set('0')
#             print(self.statlist[0].get(),self.statlist[1].get(),self.statlist[2].get(),self.statlist[3].get(),self.statlist[4].get(),self.statlist[5].get(),self.statlist[6].get(),self.statlist[7].get())
            #error here. see data structures: https://docs.python.org/3/tutorial/datastructures.html
    
    #This function takes in (x,y) coordinates (upper left hand corner) of a triangle
    #and returns the two opposite corners of a scaled-down ROI
    def calculate_ROI_corners(self, x, y, w, h):
        #this should be more of scaling down the bounding rects and returning the opposite corners of a rect
        #(i.e. upper left and lower right corners)
        #specify the centres first
        [cX, cY] = [x+(w/2), y+(h/2)]
        #upper left corner calc
        Rx1 = cX - (w*(center_tolerance/2))
        Rx1 = round(Rx1, 0)
        Ry1 = cY - (h*(center_tolerance/2))
        Ry1 = round(Ry1, 0) #in case of float, pixel data cannot accept float
        #apply an inverted calculation for the opposite corner
        Rx2 = cX + (w*(center_tolerance/2))
        Rx2 = round(Rx2, 0)
        Ry2 = cY + (h*(center_tolerance/2))
        Ry2 = round(Ry2, 0)
        return [int(Rx1), int(Ry1), int(Rx2), int(Ry2)] 
        
    def send_command(self):
        print('Command sent! Clearing all status...')
        
        [value_hex, value_bin] = self.convert_to_string()
        self.serialPort.Send(value_hex)
        
        print('String sent! string is: ', value_hex, value_bin, '\nTime surpassed:', (time.time() - self.temp))
        
        self.temp = time.time()
        #refreshes every 1.5 seconds, overriding the button function call
        self.window.after(self.senddelay, self.send_command)
        
    #can reuse this function (renamed update status or something)
    def dummy_button_press(self):
        ID=rd.randint(0,7)
        if self.statlist[ID].get() == '0':
            self.statlist[ID].set('1')
        else:
            self.statlist[ID].set('0')
    
    def set_darkbg(self):
        if self.darkbg == True:
            self.darkbg = False
        elif self.darkbg == False:
            self.darkbg = True
        print('Dark Background: ', self.darkbg)
        self.textbox.insert('1.0','Dark Background: {}\n'.format(self.darkbg))
    
    #function call for returning darkbg True/false. called at overlay option in mould_detection
    def get_darkbg(self):
        return self.darkbg
    
    #function call for setting overlay true/false from overlay button. called at __init__
    def set_overlay(self):
        if self.overlay == True:
            self.overlay = False
        elif self.overlay == False:
            self.overlay = True
        print('Overlay: ', self.overlay)
        self.textbox.insert('1.0','Overlay: {}\n'.format(self.overlay))
    
    #function call for returning overlay True/false. called at overlay option in mould_detection
    def get_overlay(self):
        return self.overlay
    
    #function call for setting thresh values, called at spinboxes in __init__
    def set_thresh(self):
        #get the value stored in the slider boxes
        self.thresh_px_hi = self.sliders_px_hi.get()
        print("current hi thresh px value: ",self.thresh_px_hi)
        self.thresh_px_lo = self.sliders_px_lo.get()
        print("current low thresh px value: ",self.thresh_px_lo)
        self.thresh_rd_hi = self.sliders_rd_hi.get()
        print("current hi thresh rd value: ",self.thresh_rd_hi)
        self.thresh_rd_lo = self.sliders_rd_lo.get()
        print("current low thresh rd value: ",self.thresh_rd_lo)
    
    #function call for getting the current thresh values. called every time at mould_detection()
    def get_thresh(self):
        return [int(self.thresh_px_lo), int(self.thresh_px_hi), int(self.thresh_rd_lo), int(self.thresh_rd_hi)]
    
    #function call for snapshot button
    def snapshot(self):
        frame = self.feed
        cv2.imwrite("conveyor-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print("Snapshot taken! Directory:")
        print("conveyor-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg")
    
    def update(self):
        #get a frame from video source
        ret,frame = self.vid.get_frame()
        
        if ret:
            frame = self.mould_detection(frame)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0,0, image = self.photo, anchor = tkinter.NW)
            
        self.window.after(self.delay, self.update)
    
    def mould_detection(self,frame):
        image = frame
        #initialising self.feed to current frame for debugging
        #program complains when there's no initial value for self.feed (argument called before declaration)
        self.feed = frame
        
        #import thresh values for everything from self.get
        [pxthresh_low, pxthresh_high, r_low, r_high] = self.get_thresh()
        
        #import boolean values from self.get
        darkbg =  self.get_darkbg()
        overlay = self.get_overlay()
        
        #image processing algorithm starts here
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        #this is for deciding if the background is dark or light
        #darkbg == True means there is a dark background behind OOI, false means light background
        if darkbg:
            thresh = cv2.threshold(gray, v_thresh, 255, cv2.THRESH_BINARY)[1]
        else:
            thresh = cv2.threshold(gray, v_thresh, 255, cv2.THRESH_BINARY_INV)[1]
        
        labels = measure.label(thresh, neighbors=8, background=0)
        
        #Gaussian blur used for more precise image mapping, i.e. blurring so that the light and dark
        #pixels clump together, giving us a good region of interest. will be filtered further
        #using thresholds.
        blur = cv2.GaussianBlur(gray,(5,5),0)
        
        #thresholding with BINARY and OTSU thresholding. recommended in some website I forgot to credit :(
        #edit 12/1/19 WHY DID I OVERWRITE THE THRESH??????
#         ret3,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#         if ret3:
#             thresh = th3
        
        #init masks in ndarray format (compatible with format of frames obtained from 
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
                
        #contour processes which I never really got, hehe
        #this should detect the contours of the OOI and highlight them for us
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        #debugging step for when there's no detectable objects/holes
        try:
            cnts = contours.sort_contours(cnts)[0]
        except:
#             print("No object detected within threshold!\nCheck:\n1)Threshold values, and\n2)Debugging steps")
            '''
            optional, can be included in final version:
            break
            '''
            
        '''
        more filtering for noise should be added here. should take the average number of times the pixel coords appear within frame
        and take those only as the OOI.
        
        edit 11/1/19 this might be a little difficult to implement? involves dynamic lists which shouldn't be too hard but speed is
        a factor in this implementation so maybe not? got another ROI implementation coming which should overcome this problem
        '''
        
        #loop over contours, identify which ones fit all thresh values, highlight them with rectangles and circles,
        #return their centers and dimensions (radius, height, width, etc.) and print them on each frame with labels
        k = 0
        for i, c in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            ((cX, cY), radius) = cv2.minEnclosingCircle(c)
            
            #draw outlines of ROIs
            for i, j in enumerate(self.ROIs):
                cv2.rectangle(image, (j[0],j[1]), (j[2], j[3]), (255,0,0), 2)
            #if within specified radius, might be wise to renumber the bounding boxes.
            if radius < r_high and radius > r_low:
                if overlay and y > y_thresh:
#                     cv2.circle(image, (int(cX), int(cY)), int(radius), (0,0,255), 3)
                    cv2.putText(image, "mold # {}".format(k+1), (x,y -15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,255), 2)
                    cv2.rectangle(image, (int(x), int(y)), (int(x+w), int(y+h)), (255,0,0), 2)
                    self.update_status(cX, cY)
                    k+=1
            
                if cX > (cam_width/2):
                    coordX = (cX - (cam_width/2))/d
                else:
                    coordX = -((cam_width/2) - cX)/d
            
                coordY = ((cam_height-20) - cY)/d
                [coordX, coordY] = [round(coordX, 2), round(coordY, 2)]
                
                #converting h,w to real sizes from pixel size. 
                [h,w] = [round(h/d, 2), round(w/d, 2)]
                area = round(h*w, 2)
                #check for overlay
                if overlay:
                    cv2.putText(image, "centers: ({},{})".format(coordX, coordY), (int(cX - radius),int(cY +radius) + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    cv2.putText(image, "h,w: ({},{})".format(h, w), (int(cX - radius),int(cY +radius) + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    cv2.putText(image, "area: ({})".format(area), (int(cX - radius),int(cY +radius) + 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0,255), thickness = 1)
                    
                #principle axes, with working center
                cv2.line(image, (0, int(cam_height-20)), (cam_width, int(cam_height-20)), color = 255)
                cv2.line(image, (int(cam_width/2), 0), (int(cam_width/2), cam_height), color = 255)
                cv2.circle(image, (int(cam_width/2), int(cam_height-20)), 5, (255, 0, 0), 1)
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
    App(tkinter.Tk(), "Conveyor GUI",cam, comport, baud) #omitted serial_rx_tx.SerialPort() from argument 3 after cam
    
if __name__ == "__main__":
    main()
    
    
    
    
    
    
