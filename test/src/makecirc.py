'''
Created on 4 Jan 2019

@author: sudoer
@source: https://github.com/sudoroom/robotools/blob/master/makecirc.py

code for interacting with Yasnac ERC Robot I think?
linked to header file (import source) erc.py

'''
#!/usr/bin/python
import os,sys,math # for reading/writing files, and sine, cosine and pi functions
from datetime import datetime, date, time # so we can put datetime in program
import erc # for talking to the robot, from https://github.com/glvnst/yasnac/tree/master/remote
robot = erc.ERC() # instance of talking to the robot
erc.DEBUG = False # tell erc.py not to dump debugging data to screen

circle_radius = ((23-6.5)/2) # in millimeters
circle_steps = 13 # number of points specified along the circle
startAboveDistance = 50 # how far above homing point the first move should be
startAboveSpeed = 46 # how fast to move to above point
descendToEntryPointSpeed = 46 # just moving from above to before starting to cut
cutDepth = 10 # in millimeters, how far below present robot position to cut
cutSpeed = 11 # 11 23 46 etc 187
num_pos = 3 + (circle_steps - 1) # total number of coordinates including circle steps
programName = 'MAKECIRC' # what the program will be called inside the robot

Cnum = 0 # coordinate number or MOV number starts at 0, used for writing robot program

outFile = open(programName+'.JBI','w') # write a file to upload to the robot

def writeFileAndPrint(data):
    global outFile
    outFile.write(data)
    sys.stdout.write(data)

def writeHeader(num_pos,jobName): # write the beginning part of a standard robot job
    writeFileAndPrint('/JOB\x0d\x0a//NAME '+jobName+'\x0d\x0a//POS\x0d\x0a///NPOS ')
    writeFileAndPrint(str(num_pos))
    writeFileAndPrint(',0,0,0\x0d\x0a///TOOL 0\x0d\x0a///RECTAN\x0d\x0a///RCONF 0,0,0,0,0\x0d\x0a')

def writeCoord(x,y,z,angle): # write a coordinate to the robot program
    global Cnum
    writeFileAndPrint('C'+str(Cnum).zfill(3)+'='+'%0.3f,%0.3f,%0.3f,' % (x,y,z)+angle+'\x0d\x0a')
    Cnum += 1

def writeMain(): # write the part after coordinates and before instructions
    global Cnum
    Cnum = 0 # reset the counter for the main part of the robot program
    writeFileAndPrint('//INST\x0d\x0a///DATE ')
    writeFileAndPrint(datetime.now().strftime("%Y/%m/%d %H:%M")) # 2016/08/02 21:44
    writeFileAndPrint('\x0d\x0a///ATTR 0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0\x0d\x0a///FRAME BASE\x0d\x0aNOP\x0d\x0a*1\x0d\x0a')

def writeLine(text): # write an arbitrary instruction in the robot program
    writeFileAndPrint(text+'\x0d\x0a')

def writeMOVL(velocity): # write a linear movement command to the robot program
    global Cnum
    writeFileAndPrint('MOVL C'+str(Cnum).zfill(3)+' V='+str(velocity)+' CONT\x0d\x0a')
    Cnum += 1

def writeMOVC(velocity): # write a circular movement command to the robot program
    global Cnum
    writeFileAndPrint('MOVC C'+str(Cnum).zfill(3)+' V='+str(velocity)+' CONT\x0d\x0a')
    Cnum += 1

def uploadFile(filename): # upload a file to the robot
    global robot
    rootname = erc.filename_to_rootname(filename)
    remote_files = robot.execute_command("RJDIR *")
    if rootname in remote_files:
        print ('A job named "{}" already exists on the robot, it will '
           'now be deleted to enable this upload').format(rootname)
        robot.execute_command("DELETE {}".format(rootname))
    print ("putting " + filename)
    return robot.put_file(filename)

def main():
    #RPOS = ['500.000', '200.000', '800.000', '-80.46', '-81.78', '-77.02', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    print('asking robot for its coordinates, robot must be in REMOTE mode')
    RPOS = robot.execute_command('RPOS') # ask the robot its present position, directly above the center of the circle
    print(RPOS)
    x = float(RPOS[0]) # retrieve values from robot's response to RPOS query
    y = float(RPOS[1])
    z = float(RPOS[2])
    angle = ','.join(RPOS[3:6]) # keep the angle a string since we're not using it as numbers
    writeHeader(num_pos,programName) # write the beginning of the robot program
    writeCoord(x,y,z+startAboveDistance,angle) # go to the position above the circle center
    writeCoord(x+circle_radius,y,z,angle) # after PAUSE, go to directly above the circle edge
    writeCoord(x+circle_radius,y,z-cutDepth,angle) # then cut 1st step of circle by moving straight down
    for i in range(1,circle_steps): # calculate coordinates for all remaining steps of the circle cut
        rads = 2 * math.pi / (circle_steps - 1) * i # how far around the circle are we, in radians
        writeCoord(x+circle_radius*math.cos(rads),y+circle_radius*math.sin(rads),z-cutDepth,angle)
    writeMain() # before we can write the instructions of the robot program
    writeMOVL(startAboveSpeed) # move to first coordinate at the appropriate speed
    writeLine('PAUSE') # stop the program until the operator hits the GO button again
    writeMOVL(descendToEntryPointSpeed) # descend to the point right above the edge of the circle
    writeMOVL(cutSpeed) # cut straight down into the first point of the circle
    for i in range(1,circle_steps): # cut the rest of the circle step by step
        writeMOVC(cutSpeed)
    writeLine('JUMP *1') # at the end of the program, go to the first position and ready to run again
    writeLine('END') # goes at the end of every robot program
    outFile.close()
    print('asking robot to receive '+outFile.name)
    print('Errors uploading: '+str(uploadFile(outFile.name)))

if __name__ == "__main__":
    main()
'''
C000=764.569,-155.385,-535.165,-98.01,-83.01,-59.58
C001=764.569,-155.385,-585.165,-98.01,-83.01,-59.58
C002=756.319,-155.385,-595.165,-98.01,-83.01,-59.58
C003=764.569,-147.135,-595.165,-98.01,-83.01,-59.58
C004=772.819,-155.385,-595.165,-98.01,-83.01,-59.58
C005=756.319,-155.385,-595.165,-98.01,-83.01,-59.58
//INST
///DATE 2016/08/02 21:44
///ATTR 0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0
///FRAME BASE
NOP
*1
MOVL C000 V=46.0 CONT
PAUSE
MOVL C001 V=11.0 CONT
MOVC C002 V=11.0 CONT
MOVC C003 V=11.0 CONT
MOVC C004 V=11.0 CONT
MOVC C005 V=11.0 CONT
JUMP *1
END
'''