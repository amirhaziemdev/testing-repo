#!/usr/bin/env python

import rospy
from std_msgs.msg import String

def callback():
	rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

def listener():
	rospy.init_node('listener', anonymous=True)
	rospy.Subscriber("chatter", String, callback)

	#Spin keeps Pyton from exiting until node is stopped
	rospy.spin()

if __name__ == "__main__":
	listener()