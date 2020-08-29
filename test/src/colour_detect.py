#!/usr/bin/env python

from __future__ import print_function
import rospy
from geometry_msgs.msg import Twist
import math
import time
from std_srvs.srv import Empty
import numpy as np
import cv2

AREA_SIZE = 800 #in pixels?
#expected frame sizes
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_WIDTH_HALF = int(FRAME_WIDTH/2)
FRAME_HEIGHT_HALF = int(FRAME_HEIGHT/2)
CENT_BOX_SIZE = 50

cap = cv2.VideoCapture(0)

def main():
	try:
		#initialise node
		rospy.init_node('turtlebot_colour_detect', anonymous=True)
	except rospy.ROSInterruptException:
		rospy.loginfo("Node terminated")

	while True:
		ret, frame = cap.read()
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		lower_yellow = np.array([20,110,110])
		upper_yellow = np.array([40,255,255])

		yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

		(contours,_) = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		#draw central bounding box
		frame = cv2.rectangle(frame, (FRAME_WIDTH_HALF-CENT_BOX_SIZE,FRAME_HEIGHT_HALF-CENT_BOX_SIZE), 
			(FRAME_WIDTH_HALF+CENT_BOX_SIZE,FRAME_HEIGHT_HALF+CENT_BOX_SIZE), (255,0,255), 5)
		centr_bound_x = [FRAME_WIDTH_HALF-CENT_BOX_SIZE,FRAME_WIDTH_HALF+CENT_BOX_SIZE]
		centr_bound_y = [FRAME_HEIGHT_HALF-CENT_BOX_SIZE,FRAME_HEIGHT_HALF+CENT_BOX_SIZE]
		for contour in contours:
			area = cv2.contourArea(contour)

			if(area>AREA_SIZE):
				x,y,w,h = cv2.boundingRect(contour)
				centre = (x+(w/2), y+(h/2)) #determining centre of boundingRect
				frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 5)
				# print("Centre - x: {}, y: {}".format(centre[0],centre[1]))
				# print("Boundaries - x:{},{}  y:{},{}".format(centr_bound_x[0],centr_bound_x[1],centr_bound_y[0],centr_bound_y[1]))

				if (centre[0] in range(centr_bound_x[0],centr_bound_x[1])) & (centre[1] in range(centr_bound_y[0], centr_bound_y[1])):
					print("Within bounding box!\n")

				distance_from_centre = [(centre[0]-FRAME_WIDTH_HALF),-(centre[1]-FRAME_HEIGHT_HALF)]

				print("Distance to move:({},{})\n".format(distance_from_centre[0],distance_from_centre[1]))
				# else:
				# 	print("Outside bounding box\n")

		cv2.imshow("Colour Tracking", frame)

		if cv2.waitKey(30) & 0xFF == ord('q'):
			break

	cv2.destroyAllWindows()
	cap.release()

def move(speed, distance, is_forward):
	#declare a Twist message to send velocity commands
    velocity_message = Twist()
    #get current location 


    if (speed > 0.4):
        print 'speed must be lower than 0.4'
        return

    if (is_forward):
        velocity_message.linear.x =abs(speed)
    else:
    	velocity_message.linear.x =-abs(speed)

    distance_moved = 0.0
    loop_rate = rospy.Rate(10) # we publish the velocity at 10 Hz (10 times a second)    
    cmd_vel_topic='/cmd_vel_mux/input/teleop'
    velocity_publisher = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)

    t0 = rospy.Time.now().to_sec()

    while True :
            rospy.loginfo("Turtlesim moves forwards")
            velocity_publisher.publish(velocity_message)

            loop_rate.sleep()
            t1 =  rospy.Time.now().to_sec()
            #rospy.Duration(1.0)
            
            distance_moved = (t1-t0) * speed
            print  distance_moved               
            if  not (distance_moved<distance):
                rospy.loginfo("reached")
                break
    
    #finally, stop the robot when the distance is moved
    velocity_message.linear.x =0
    velocity_publisher.publish(velocity_message)

def rotate (angular_speed_degree, relative_angle_degree, clockwise):
    

    velocity_message = Twist()
    velocity_message.linear.x=0
    velocity_message.linear.y=0
    velocity_message.linear.z=0
    velocity_message.angular.x=0
    velocity_message.angular.y=0
    velocity_message.angular.z=0

    angular_speed=math.radians(abs(angular_speed_degree))

    if (clockwise):
        velocity_message.angular.z =-abs(angular_speed)
    else:
        velocity_message.angular.z =abs(angular_speed)

    angle_moved = 0.0
    loop_rate = rospy.Rate(10) # we publish the velocity at 10 Hz (10 times a second)    
    cmd_vel_topic='/cmd_vel_mux/input/teleop'
    velocity_publisher = rospy.Publisher(cmd_vel_topic, Twist, queue_size=10)

    t0 = rospy.Time.now().to_sec()

    while True :
        rospy.loginfo("Turtlesim rotates")
        velocity_publisher.publish(velocity_message)

        t1 = rospy.Time.now().to_sec()
        current_angle_degree = (t1-t0)*angular_speed_degree
        loop_rate.sleep()

        print 'current_angle_degree: ',current_angle_degree
                       
        if  (current_angle_degree>relative_angle_degree):
            rospy.loginfo("reached")
            break

    #finally, stop the robot when the distance is moved
    velocity_message.angular.z =0
    velocity_publisher.publish(velocity_message)


if __name__=="__main__":
	main()
	# do stuff