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
#import tensorflow
#load our saved model
from keras.models import load_model

from keras import backend as K # Destroys the current TF graph and creates a new one






#helper class
import utils
from utils import Steuerbits_16, Kommunikation
Geschwindigkeit = 25 #35 

stop_flag = False
import cv2
import time


Kamera = utils.openCam()



def calc_steering(model_file):





	#load model
	model = load_model(model_file)

	print ("\n\n\n ")
	#Kamera = utils.openCam()
	print ("|\n|...Feuer frei! --> \n|")
	while True:
		if (not stop_flag):
			#time1 = time.process_time()
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
			#print(stop_flag)

			Kommunikation.sendeAnST(Geschwindigkeit,0.0,0.0,steering_angle,Steuerbits_16) # Sende ueber UART an ST
			#time2 = time.process_time()
			#loop_time = time2 - time1
			#print(loop_time)
			# TODO auf Tread legen, sonst wird die loop ausgebremst, da der ST nur alle 100 ms daten zurueck schickt
			#EmpfangVonST=Kommunikation.empfangeVonST()					# Uart Daten einlesen
			#print("Geschwindigkeit: "+ str(EmpfangVonST['MomentanGeschwindigkeit']) + "m/s" )

		if stop_flag:
			K.clear_session() ## Destroys the current TF graph and creates a new one
			break
	

	print("|...Thread beendet!")

def set_stop_flag():
	global stop_flag 
	stop_flag = True
	#print("gesetzt")

def reset_stop_flag():
	global stop_flag 
	stop_flag = False
	#print("zurückgesetzt")

def set_autonomer_modus():
	global Steuerbits_16
	Steuerbits_16[0]=1 
	time.sleep(0.25)
	Steuerbits_16[0]=0 	#nicht dauerhaft auf 1 steuern, sonst kann der ST selber den
	print("|...Befehl autonomer Modus gesendet")			#autonomen modus nicht unterbrechen


def lese_von_ST():
	
	return Kommunikation.empfangeVonST()


  
