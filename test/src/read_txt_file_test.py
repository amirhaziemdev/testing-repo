'''
Created on 4 Feb 2019

@author: Amir Haziem Razali
Code for reading configurations from text file. Current text file directory is C:\\Users\\USER\\git\\repository\\test\\src\\configs.txt
Will be implemented in main conveyor_GUI
Mainly uses python's dictionary capability

Update 19/2/2019
- No changes since last implementation
- This method has been implemented in main conveyor code
'''

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
    
print(my_constants['f'])
f.close()

