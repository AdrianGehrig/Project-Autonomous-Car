
from imutils.video import WebcamVideoStream
import imutils
import cv2

vs = WebcamVideoStream(src="/dev/video1").start()
while True:

	
	frame = vs.read()
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
