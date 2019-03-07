'''
Created on 15 Jan 2019

@author: Amir Haziem Razali
'''

import serial

ser = 0

def init_serial():
    COMNUM = 3
    global ser
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM'+str(COMNUM)
    
    ser.timeout =10
    ser.open()
    
    if ser.isOpen():
        print('Open:', ser.portstr)


init_serial()
temp = input('Type what you want to send, and then hit enter:\r\n')
ser.write(temp.encode('utf-8'))

while True:
    bytes = ser.readline()
    print('You sent: ', bytes.decode())