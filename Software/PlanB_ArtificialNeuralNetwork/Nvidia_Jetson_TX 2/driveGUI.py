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
steering_angle=0
Fummelfaktor_Stellwinkel=1

Kamera = utils.openCam()



def calc_steering(model_file):
	global steering_angle
	global imageAnzeigbar
	global Fummelfaktor_Stellwinkel

	#load model
	model = load_model(model_file)

	print ("\n\n\n ")
	#Kamera = utils.openCam()
	print ("|\n|...Hauptschleife gestartet\n|...Feuer frei! --> \n|")
	while True:
		if (not stop_flag):
			#time1 = time.process_time()
			frame = utils.grabFrame(Kamera)	# hole aktuellen Frame

			frame=cv2.resize(frame, (320,240))	 
		
		



			image = np.asarray(frame)       # from PIL image to numpy array
			imageAnzeigbar = utils.preprocessKameraStream(image) # apply the preprocessing
		
			image = np.array([imageAnzeigbar])       # the model expects 4D array

		


     			# predict the steering angle for the image
			steering_angle = float(model.predict(image, batch_size=1))*Fummelfaktor_Stellwinkel
			#print (steering_angle)
			#print(stop_flag)

			#Geschwindigkeit_variabel = Geschwindigkeit*(1-(abs(steering_angle)/25))
			#print(Geschwindigkeit_variabel)
			#Kommunikation.sendeAnST(Geschwindigkeit_variabel,0.0,0.0,steering_angle,Steuerbits_16) # Sende ueber UART an ST
			
			
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
	print("|...> Befehl autonomer Modus gesetzt")			#autonomen modus nicht unterbrechen
	
	
def set_manueller_modus():
	global Steuerbits_16
	Steuerbits_16[1]=1 
	time.sleep(0.25)
	Steuerbits_16[1]=0 	#nicht dauerhaft auf 1 steuern, sonst kann der ST selber den
	print("|...> Befehl manueller Modus gesetzt")			#autonomen modus nicht unterbrechen


def lese_von_ST():
	global Empfang
	Empfang= Kommunikation.empfangeVonST()
	
	return Empfang

def set_Gaspedal_Stellung(soll_Stellung):
	
	global Geschwindigkeit
	Geschwindigkeit=soll_Stellung
	print("|...Gaspedal Stellung: "+str(Geschwindigkeit)+ "%")

def show_Frame():
	global frame
	print("|...Stream Thread gestartet")
	while True:
		try: # bevor der autonome modus nicht gestartet wird gibt es noch kein bild, da die hauptschelife noch nicht los läuft		
			
			image_anzeigbar_in_RGB=cv2.cvtColor(imageAnzeigbar, cv2.COLOR_YUV2BGR)	# weil bild noch in yuv und die Anzeigefunktion ein RGB Bild erwartet obach scheiss OpenCV arbeitet mit BGR
			image_anzeigbar_in_RGB=cv2.resize(image_anzeigbar_in_RGB, (200*6, 66*6), cv2.INTER_AREA)		# weil ma auf dem kleinen bild (66x200) nix gsehen hat	
			cv2.imshow("Aktuelles Bild",image_anzeigbar_in_RGB)# preprocesstes Bild anzeigen
			key = cv2.waitKey(1) & 0xFF # Aktualisiert Bild Anzeige
		except:
			pass
		
def get_model_steering_angle():
	return steering_angle


def set_Fummelfaktor_Stellwinkel(Slider_Stellung):
	global Fummelfaktor_Stellwinkel 
	Fummelfaktor_Stellwinkel=Slider_Stellung
	print("|...Fummelfaktor Stellwinkel: "+str(Fummelfaktor_Stellwinkel))
	


  
