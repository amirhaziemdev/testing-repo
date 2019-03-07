'''
Created on 28 Jan 2019

@author: Amir Haziem Razali
Code for testing write to modbus. Should be pretty simple and straightforward.
This can then be incorporated into the main conveyor GUI code.

Version 19/2/2019
- Still working with Modbus Slave application
- No major changes
- Has been implemented in main conveyor code
'''

import pymodbus
from pymodbus.client.sync import ModbusSerialClient
import random as rd
import tkinter as tk

start_address = 2040

class Modbus():
    def __init__(self, window, window_title, port, baudrate):
        self.window = window
        self.window.title(window_title)
        self.port = port
        self.baudrate = baudrate
        self.client = ModbusSerialClient(method='rtu', port=self.port, baudrate=self.baudrate, parity = 'O')
        
        self.myList = [0,0,0,0,0,0,0,0]
        
        self.delay = 1200 #ms
        self.update()
        self.window.mainloop()
        
    def update(self):
        temp = rd.randint(0,7)
        print(self.assign(temp))
        self.send_IO()
        self.window.after(self.delay, self.update)
        
    def send_IO(self):
        for i,j in enumerate(self.myList):
            if self.myList[i] == 1:
                self.client.write_coil(start_address+i, value=1, unit=1)
#                 print('Writing 1 to address:', start_address+i)
            elif self.myList[i] == 0:
                self.client.write_coil(start_address+i, value=0, unit=1)
#                 print('Writing 0 to address:', start_address+i)
        
    def assign(self, temp):
        for i in range(temp):
            j = rd.randint(i,7)
            if self.myList[j] == 1:
                self.myList[j] = 0
            elif self.myList[j] == 0:
                self.myList[j] = 1
        return self.myList
    
def main():
    Modbus(tk.Tk(), 'Modbus Testing','COM4',9600)   
    return 0
    

if __name__ == '__main__':
    main()