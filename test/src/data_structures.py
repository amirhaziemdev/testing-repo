'''
Created on 14 Jan 2019

@author: Amir Haziem Razali
This program is for testing various data structures before implementation
'''

import random as rd

center_tolerance = 0.33


def main():
    
    ROI = []
    ROIProcessed = []
    status = [0,0,0,0,0,0,0,0]
    ROI1 = [x, y, w, h] = [10, 10, 5, 5]
    [x1, y1, x2, y2] = [10, 10, 80, 80]
    for i in range(8):
        temp = [rd.randint(1,90),rd.randint(1,90),rd.randint(1,90),rd.randint(1,90)]
        ROI.append(temp)

    print(ROI)
    print(ROI[1])
    print(ROI[1][1])
    
    
    for i, j in enumerate(ROI):
        print(ROI[i])
        ROIProcessed.append(calculate_ROI_corners(j[0], j[1], j[2], j[3]))
        for k, l in enumerate(j,1): #second argument in enumerate specifies which index the function starts with. default is 0
            print(k,'\t',l)
            if i%2==1:
                status[i] = 1
            
    print('End of first loop')
    print(ROIProcessed)
    print("status:", status)
    
    value = '10110110'
    value = int(value, base=2)
    value = hex(value)
    print('value is:',value, type(value))
    return 0

def calculate_ROI_corners(x, y, w, h):
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
        return [Rx1, Ry1, Rx2, Ry2]
if __name__=="__main__":
    main()