import numpy as np
import cv2



# this function grabs an undistorted frame

def grabFrame():
	cap = cv2.VideoCapture("/dev/video1")
	#cap = cv2.VideoCapture("/dev/video0") #fuer Testzwecke in einer VM	
	for x in range(0, 3):
			ret, frame = cap.read()
			#undist = cv2.undistort(frame, mtx, dist, None, mtx)
			cv2.imwrite("frame.jpg", frame)
			

grabFrame() 
		
	

