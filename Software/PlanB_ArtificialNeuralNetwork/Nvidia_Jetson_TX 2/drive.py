#parsing command line arguments
import argparse
#decoding camera images
import base64
#for frametimestamp saving
from datetime import datetime
#reading and writing files
import os
#high level file operations
import shutil
#matrix math
import numpy as np
#image manipulation
from PIL import Image

#load our saved model
from keras.models import load_model

#helper class
import utils
from utils import Steuerbits_16, Kommunikation
Geschwindigkeit =15 


import cv2
import time

def calc_steering():
	parser = argparse.ArgumentParser(description='Remote Driving')
	parser.add_argument(
        'model',
        type=str,
        help='Path to model h5 file. Model should be on the same path.'
    )
	args = parser.parse_args()

	#load model
	model = load_model(args.model)

	print ("\n\n\n ")
	Kamera = utils.openCam()
	print ("|\n|...Feuer frei! --> \n|")
	while True:
		time1 = time.process_time()
		frame = utils.grabFrame(Kamera)	# hole aktuellen Frame
		#cv2.imshow("Aktuelles bildle", frame)
		#key = cv2.waitKey(1) & 0xFF 
		frame=cv2.resize(frame, (320,240))	 
		
		



		image = np.asarray(frame)       # from PIL image to numpy array
		image = utils.preprocessKameraStream(image) # apply the preprocessing
		
		#cv2.imshow("Aktuelles Bild", image)# preprocesstes Bild anzeigen
		#key = cv2.waitKey(1) & 0xFF # Aktualisiert Bild Anzeige
		
		image = np.array([image])       # the model expects 4D array

		


     	# predict the steering angle for the image
		steering_angle = float(model.predict(image, batch_size=1))
		#print (steering_angle)
			
		Kommunikation.sendeAnST(Geschwindigkeit,0.0,0.0,steering_angle,Steuerbits_16) # Sende ueber UART an ST
		time2 = time.process_time()
		loop_time = time2 - time1
		#print(loop_time)
		# TODO auf Tread legen, sonst wird die loop ausgebremst, da der ST nur alle 100 ms daten zurueck schickt
		#EmpfangVonST=Kommunikation.empfangeVonST()					# Uart Daten einlesen
		#print("Geschwindigkeit: "+ str(EmpfangVonST['MomentanGeschwindigkeit']) + "m/s" )



calc_steering()








  
