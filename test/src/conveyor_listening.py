'''
Created on 22 Jan 2019

@author: Amir Haziem Razali
Mechanism for listening to any data sent by conveyor_gui.py
Will also convert HEX code into conveyor positions
e.g.
0xFF -> 1111 1111
0xEF -> 1110 1111
0xE1 -> 1110 0001

'''

import tkinter
import serial_rx_tx
from tkinter.scrolledtext import ScrolledText


class ListenApp():
    def __init__(self, window, window_title, serialPort, portNum, baudrate):
        self.window = window
        self.window.title = window_title
        self.portNum = 'COM'+str(portNum)
        self.baudrate = baudrate
        
        self.serialPort = serialPort
        self.serialPort.RegisterReceiveCallback(self.onReceiveSerialData)
        
        comportlabel = tkinter.StringVar()
        comportlabel.set('COM Port')
        self.comportLabel = tkinter.Label(window, textvariable = comportlabel)
        self.comportLabel.grid(row=0,column=0)
        
        comportentry = tkinter.StringVar(value='5')
        self.comportEntry = tkinter.Entry(window, textvariable=comportentry)
        self.comportEntry.grid(row=0,column=1)
        
        baudlabel = tkinter.StringVar()
        baudlabel.set('Baud rate')
        self.baudLabel = tkinter.Label(window, textvariable = baudlabel)
        self.baudLabel.grid(row=1,column=0)
        
        baudentry = tkinter.StringVar(value='9600')
        self.baudEntry = tkinter.Entry(window, textvariable=baudentry)
        self.baudEntry.grid(row=1,column=1)
        
        self.frame = tkinter.Frame(window, bg='cyan').grid(row=0,column=3,rowspan=10,columnspan=1)
        self.textbox = ScrolledText(self.frame, wrap='word',width=40)
        self.textbox.grid(row=0,column=3,rowspan=10,columnspan=1)
        
        self.openPortButton = tkinter.Button(window, text='Open COM Port', command=self.openPort).grid(row=2,column=1)
        self.closePortButton = tkinter.Button(window, text='Close COM Port', command=self.closePort).grid(row=3,column=1)

        self.delay = 50 #ms
        self.update()
        
    def setBaudrate(self):
        temp = self.baudEntry.get()
        self.baudrate = temp
    
    def getBaudrate(self):
        return self.baudrate
    
    def setPortNum(self):
        temp = self.comportEntry.get()
        self.portNum = 'COM'+str(temp)
    
    def getPortNum(self):
        return self.portNum
    
    def openPort(self):
        self.setPortNum()
        self.setBaudrate()
        try:
            self.serialPort.Open(self.portNum,self.baudrate)
            self.textbox.insert('1.0','COM Port {} opened!\nBaudrate:{}\n'.format(self.portNum,self.baudrate))
            print('COM Port {} opened!'.format(self.portNum))
        except:
            self.textbox.insert('1.0','COM Port {} open failed.\n'.format(self.portNum))
    
    def closePort(self):
        self.serialPort.Close()
        self.textbox.insert('1.0', 'COM Port {} closed! You may exit the program now\n'.format(self.portNum))
        print('COM Port {} closed! You may exit the program now'.format(self.portNum))
    
    def onReceiveSerialData(self, message):
        str_message = message.decode("utf-8")
        str_message = int(str_message,0)
        str_message = bin(str_message)[2:].zfill(8)
        self.textbox.insert('1.0', str_message+'\n')
        
    def update(self):
        self.window.mainloop()
        self.window.after(self.delay, self.update)


def main():
    ListenApp(tkinter.Tk(), 'Listening', serial_rx_tx.SerialPort(), 4, 9600)

if __name__=="__main__":
    main()
    