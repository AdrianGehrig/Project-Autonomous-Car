import time

import numpy as np
import cv2
import sys
#from matplotlib import pyplot as plt

from bitarray import bitarray					# Bitarray fuer Steuerbits
import KommunikationUart as MyModule				# Klasse fuer UART Kommunikation
Kommunikation=MyModule.KommunikationUart() 			# Objekt der Klasse KommunikationUart Erzeugen

Steuerbits_16=bitarray(16,endian='little')			# Steuer Bitarray erzeugen
Steuerbits_16.setall(False)					# Alle Werte auf null setzen, da sonst zufaellige drinnen stehen
					
from imutils.video import WebcamVideoStream			# USB Bilder Bibliothek				
import imutils									


OPTIMIERUNG_EINGESCHALTET = False			# Zum aktivieren oder deaktiveren der Optimirungen #TODO Hyperparameter




##################################################################################################################################  
#	 ______           _    _   _                        	
#	|  ____|         | |  | | (_)                       	
#	| |__ _   _ _ __ | | _| |_ _  ___  _ __   ___ _ __  	
#	|  __| | | | '_ \| |/ / __| |/ _ \| '_ \ / _ \ '_ \ 	
#	| |  | |_| | | | |   <| |_| | (_) | | | |  __/ | | |	
#	|_|   \__,_|_| |_|_|\_\\__|_|\___/|_| |_|\___|_| |_|	
#
##################################################################################################################################                                                


#################################################################


def openCam():
	""" Erzeugt ein gethreadeten video stream"""
	
	print("|...Suche Kamera")			
	Kamera = WebcamVideoStream(src="/dev/video1").start()	# Erzeugt ein Kameraobjekt
	#Kamera.set(10,50)							
	#Kamera = WebcamVideoStream(src="/dev/video0").start()	
	
	return Kamera


#################################################################


def setupStream():
	""" Erzeugt Fenster fuer live Kamerastream"""
	
	windowName = "main"
	cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
	cv2.resizeWindow(windowName,1280,720)
	cv2.moveWindow(windowName,0,0)
	cv2.setWindowTitle(windowName,"Gizmo TV")
		
	showHelp = True						# Flag zum ein und ausschalten des Hilfetextes

	font = cv2.FONT_HERSHEY_PLAIN				# Fontstyle und help text inhalt
	helpText="'Esc' to Quit, '1' for camera feed, '2' for warped feed,  '3' for all stages, '4' to hide help, '9' to start autonomus mode"
        	
	
	return windowName, showHelp, helpText, font


#################################################################


def countFrames(frame_number, Kamera):
	"""Zaehle Frames; wird benoetigt, da ersten paar Frames schwarz sind"""
	
	frame = Kamera.read()					# Hole das aktuellste Frame des Kamera Objektes #TODO wird das benoetigt???
	frame_number +=1					# erhoe Zaehler um 1


	return frame_number


#################################################################


def grabFrame(Kamera):
	"""Hole das aktuellste Frame des Kamera Objektes"""

	frame = Kamera.read()  
	

	return frame 


#################################################################


def grayFrame(undistorted):
	"""Konvertiere Frame zu einem grauem Bild"""

	# Convert BGR to HSV
	hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)

	# define range of blue color in HSV ###### Hue range is [0,179], Saturation range is [0,255] and Value range is [0,255]. 
	sensitivity = 50
 	# Werte fuer GEGEN das Licht gefahren
	#lower_white = np.array([0,0,0])
	#upper_white = np.array([179,20,255])
	
	lower_white = np.array([0,0,52])
	upper_white = np.array([179,50,255])
 	# Threshold the HSV image to get only white colors
	binary = cv2.inRange(hsv, lower_white, upper_white)


	return binary


#################################################################


def undistFrame(frame):
	"""Entzerre Frame (entferne Beugung der Linse) """	# TODO Hyperparameter; bei neuer Kamera die mtx.dat und dist.dat durch distortion.py neu erzeugen

	undistorted = cv2.undistort(frame, mtx, dist, None, mtx)


	return undistorted


#################################################################


def warpFrame(trans_M, img_size, gray):
	"""Warpe Bild in Vogelperspektive"""			# TODO Hyperparameter; bei neuer Kamerastellung die trans_M.dat durch transformation_handler.py neu erzeugen
	
	warped = cv2.warpPerspective(gray, trans_M, img_size)


	return warped


#################################################################



#def binaryFrame(warped, thresh_val, max_val):
#	"""Konvertiere  gewarptes Bild zu binaeren Bild"""	
#
#	ret, binary = cv2.threshold(warped, thresh_val, max_val, cv2.THRESH_BINARY)
#
#
#	return binary

#################################################################


def checkBinary(binary, histogram_maske,histogramm_breite, thresh_val):
	"""Schaut ob das aktuelle Bild akzeptabel zur weiterverarbeitung ist, wenn nicht wird der threshold angepasst, sodass das bild aus mehr oder weniger weissen pixeln besteht"""
	
	binary_maskiert=cv2.bitwise_and(binary,histogram_maske)	# binaeres bild ausmaskieren

	percentage = (np.count_nonzero(binary_maskiert))/((histogramm_breite*histogramm_breite*3.14)/2) # weisse pixel in maske/ flaeche eines Halbkreises

	#Fehler=0.1-percentage
	#KP=100#40

	
	#thresh_val=thresh_val- ( Fehler*KP)
	#print("thresh_val: "+str(thresh_val)+ " %: "+ str(percentage))	

	if(percentage>0.15):					# Wichtig, hier muss eine Art Hysterese da sein (0.10 und 0.08) sonst wird staendig das bild angepasst... 
		thresh_val +=1#*Fehler*KP
	if(percentage<=0.08):					# ...auch wenn es ok ist aber die Berechnung der neuen polynome wird uebersprungen
		thresh_val -=1#*Fehler*KP

	#print(str(percentage*100) +"%")
	if (percentage>0.001):
		#print("OK THRESH: "+str(thresh_val)+ "percentage" +str(percentage))		
		return True, thresh_val				# Ja, mit dem aktuellen frame kann neu gerechnet werden
	else:
		#print("BAD THRESH: "+str(thresh_val)+ "percentage" +str(percentage))		
		return False, thresh_val			# Nein, mit dem aktuellen frame kann nicht neu gerechnet werden..frame verwenden vom zyklus davor, welches noch gut war


#################################################################


def getPolynoms(binary,Faktor_Meter_pro_Pixel,histogram_basis,histogramm_breite,histogramm_hoehe):
	"""Erfasse Polynome der linken und rechten Ausenspur und erzeuge deren Koeffizienten"""
	
	global histogram_maske
	
	out_img = np.dstack((binary, binary, binary))			# create new output image


	
	
	binary_maskiert=cv2.bitwise_and(binary,histogram_maske)			# binaeres bild ausmaskieren
	#cv2.imshow('Maskiert',cv2.bitwise_and(binary,histogram_maske))	# Ausschnitt live anzeigen

	histogram = np.sum(binary_maskiert, axis=0)			# Erzeuge ein Histogramm aus dem Ausschnitt(Matrix Spaltenweise aufaddieren)
	
	
	leftx_base = np.argmax(histogram)	# Maximum des Histogramms wird Startpunkt des ersten Fensters
	if leftx_base==0:			# wenn sich nichts im Histogramm befindet starte die Fenster mittig der Maske
		leftx_base=histogram_basis
	

	if OPTIMIERUNG_EINGESCHALTET == True:	
		#window_height = np.int(0.4/Faktor_Meter_pro_Pixel)	# define number of moving windwows (Optimized)
      
		nwindows = 50
		window_height = binary.shape[0]/nwindows
	else:
    
		nwindows = 50
		window_height = binary.shape[0]/nwindows	# hoehe der Fenster in pixeln Ein Fenster soll immer 40cm lang sein (2*mittelstreifen)	
	
	#nwindows = 25		# Anzahl der Fenster im Pixelbild
	
	
	#margin = int(3*0.025/Faktor_Meter_pro_Pixel)			# set the width of the windows +/- margin
	margin = int(0.09/Faktor_Meter_pro_Pixel)	

	#minpix = 25							# set minimum number of pixels found to recenter window
	minpix=10
	flaecheFenster=window_height*2*margin
	maxpix= 50*(flaecheFenster*0.07)					# Maximale weisse pixel in einem fenster, ansonsten ist es falsch


	Steigungsfaktor= window_height/(margin*2.0)*2.4			# TODO Fummelfaktor
	
	#print(Steigungsfaktor)						# Faktor um den der SteigungsTrend der Fenster multipliziert wird. 
									# Muss bei wenigen Fenstern groesser 1 sein und bei vielen Fenstern kleiner 
									# Muss bei breiten Fenstern kleiner 1 sein und bei schmalen groesser 1
									# 
									# 									
									# Ist die Steigung zu gross schwingen die Fenster um die Linie, 
									# ist sie zu klein wandern sie nicht stark genug auf die Linie zu und kommen ab

								

	# Identify the x and y positions of all nonzero pixels in the image
	nonzero = binary.nonzero()   					#returns the indicies

	nonzeroy = np.array(nonzero[0]) 				# y: in which row, bottom to top
	nonzerox = np.array(nonzero[1])					# x: in which column, left to right

	# Current positions to be updated for each window
	leftx_current = leftx_base

	

	# Create empty lists to receive left lane pixel indices
	left_lane_inds = []

	
	# Anfangstrend = 0 und anfangsbasispunkt =base_left
	delta_Trend_left=[0,0,0]
	base_left_Trend=[leftx_base,leftx_base,leftx_base]
	Trend_counter_left=0
	

	# step through each window one by one
	for window in range(nwindows):					
	#identify window boundaries in x and y
		win_y_low = binary.shape[0] - (window+1)*window_height
		win_y_high = binary.shape[0] - window*window_height
		win_xleft_low = leftx_current - margin
		win_xleft_high = leftx_current + margin


		# draw the windows on the visualization image
		if OPTIMIERUNG_EINGESCHALTET==True:
			pass
		else:
			cv2.rectangle(out_img, (win_xleft_low,win_y_low), (win_xleft_high,win_y_high), color=(0,255,0), thickness=1)		# left lane
			

		# identify the nonzero pixels in x and y within the window
		good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]		# left lane

				
		#append these indices to the lists
		left_lane_inds.append(good_left_inds)

		
				
		# If  > minpix pixels found, recenter NEXT window on its mean position
		if len(good_left_inds) > minpix and len(good_left_inds) < maxpix:
			base_left_Trend[Trend_counter_left]=leftx_current				# Basispunkt des aktuellen Fensters speichern( war Mittelwert des Fensters davor)
	
			leftx_current = np.int(np.mean(nonzerox[good_left_inds])) 			# Mittelwert des jetztigen Fensters berechnen
				
			delta_Trend_left[Trend_counter_left]=leftx_current-base_left_Trend[Trend_counter_left-1]# DeltaTrend = Mittelwert des jetztigen Fensters -Basispunkt des Fensters davor	

			leftx_current=leftx_current+int(round((sum(delta_Trend_left)/3.0)*Steigungsfaktor)) # naechstes Fenster Basis= Mittelwert des jetztigen Fensters + DeltaTrend
			
			Trend_counter_left+=1
			#Counter zurueck setzen		
			if Trend_counter_left==3:
				Trend_counter_left=0
			#print("if")

		else:	# Keine pixel in aktuellen Fenster gefunden, also: SteigungsTrend aus den letzten 3 werten beibehalten
			base_left_Trend[Trend_counter_left]=leftx_current				# Basispunkt des aktuellen Fensters speichern( war Mittelwert des Fensters davor)		
			
			leftx_current=leftx_current+int(round((sum(delta_Trend_left)/3.0)*Steigungsfaktor))# naechstes Fenster Basis= Mittelwert des jetztigen Fensters + DeltaTrend
 				
			Trend_counter_left+=1
			if Trend_counter_left==3:
				Trend_counter_left=0
			#print("else")

		
		
	

		#print("c:" +str(Trend_counter_left)+" Trends:" + str(delta_Trend_left)+" Aktuell:"+str(int(round(sum(delta_Trend_left)/3.0)))+" Basis:"+ str(leftx_current))		
	#print("\nLoop done\n\n")	
		
	
	# Concatenate the arrays of indices
	left_lane_inds = np.concatenate(left_lane_inds)



	if not left_lane_inds.any():				# TODO bug "expected non-empty vector for x" passiert wenn vektoren leer sind, weil keine polynome gebildet werden koennen
		print("|  Keine Mittellinen Polynom gefunden")
		left_fit=[0,0,320]
	else:
		# Extract lines pixel positions
		leftx = nonzerox[left_lane_inds]
		lefty = nonzeroy[left_lane_inds]
		# Fit a second order polynomial
		left_fit = np.polyfit(lefty, leftx, 2)	

	




	#### Neue basis der neuen Maske fuer naechste Iteration dahin legen, wo das Maximum in der alten Maske lag (Tracking der Linie)  

	histogram_maske = np.zeros((480,640), np.uint8)			# erzeuge leeres binary Bild
	cv2.ellipse(histogram_maske, (leftx_base,480),(histogramm_breite,histogramm_hoehe),0,0,-180,color=(255,255,255), thickness=-1) # male die Maske fuer das Histogramm in das binary		
	
	cv2.ellipse(out_img, (leftx_base,480),(histogramm_breite,histogramm_hoehe),0,0,-180,color=(0,255,0), thickness=1) #zeichne in das bunte Bild die verwendete Maske fuer das Histogram	

	return out_img, left_fit


#################################################################



def plottablePolynoms(binary, left_fit, ):
	"""Erzeuge x und y Werte zum Ploten der Polynome"""

	ploty = np.linspace(0, binary.shape[0]-1, binary.shape[0] )
	left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
	
	if OPTIMIERUNG_EINGESCHALTET == True:						# TODO Servo bug entfernen?
		pass

	else:
		# if polynom is outside of image, value is set to boundaries to prevent crash 			
		for element in range(len(ploty.astype('int'))):
			if left_fitx[element] < 0:
				left_fitx[element] = 0
			if left_fitx[element] > 639:
				left_fitx[element] = 639
			

	return ploty, left_fitx


#################################################################


def calcMiddle(binary, ploty, left_fitx,Faktor_Meter_pro_Pixel):
	"""Berechne Mittellinie aus linker Linie"""
		
	middle_fitx = np.linspace(0, binary.shape[0]-1, binary.shape[0] )				# Erzeuge leeres Array
	for element in range(len(ploty.astype('int'))):
													# punktweise an mittellinie 20 cm draufzaehlern
		middle_fitx[element] = left_fitx[element]+(int(round(0.10/Faktor_Meter_pro_Pixel)))
		
		# if polynom is outside of image, value is set to boundaries to prevent crash 			
		if middle_fitx[element] < 0:
				middle_fitx[element] = 0	
		if middle_fitx[element] > 639:
				middle_fitx[element] = 639	
		
	return middle_fitx


#################################################################


def plotPolynoms(out_img, ploty, left_fitx, middle_fitx, xin,yin):
	"""Plotte Polynome und Abweichung Zielpunkt zur Mitte"""

	if OPTIMIERUNG_EINGESCHALTET == True:		# TODO kann man hier noch mehr weg lassen?
		y=xin					# CK wird nur benoetigt, wenn einzelne pixel gezeichnet werden sollen
		x=(yin-480)*(-1)			# CK wird nur benoetigt, wenn einzelne pixel gezeichnet werden sollen	
						
		out_img[x+2,   y  ] = [0,255,0] 	#AdG
		return out_img
	else:
		out_img[ploty.astype('int'),left_fitx.astype('int')] = [0, 255, 0]
		out_img[ploty.astype('int'),middle_fitx.astype('int')] = [127, 0, 0]

 							# TODO Kuchsch'e Weisheits Erlaeuterung
		y=xin					# CK wird nur benoetigt, wenn einzelne pixel gezeichnet werden sollen
		x=(yin-480)*(-1)			# CK wird nur benoetigt, wenn einzelne pixel gezeichnet werden sollen	
	
		#Keine Ahnung, warum hier das Koordinatensystem wieder rum gedreht werden muss, wenn man ueber open CV Plottet	
		cv2.line(out_img, (y,x+5) ,(y,x-5),color=(255,0,0), thickness=1) 					# kurze Gerade auf mittellinie zeichnen
		cv2.line(out_img, (320,x+10) ,(320,x-10),color=(255,0,0), thickness=1)					# Mittellinie zeichnen
		cv2.arrowedLine(out_img, (320,x),(y,x) ,color=(255,0,0), thickness=1, tipLength=0.2)			# Abweichung zeichnen	
		

		#out_img[x+2,   y  ] = [0,255,0] 	#AdG
		#out_img[x+2,   y+1] = [0,255,0] 	#AdG
		#out_img[x+2,   y-1] = [0,255,0] 	#AdG

		#out_img[x-2,   y  ] = [0,255,0] 	#AdG
		#out_img[x-2,   y+1] = [0,255,0] 	#AdG
		#out_img[x-2,   y-1] = [0,255,0] 	#AdG

		#out_img[x,     y-2] = [0,255,0] 	#AdG
		#out_img[x+1,   y-2] = [0,255,0] 	#AdG
		#out_img[x-1,   y-2] = [0,255,0] 	#AdG

		#out_img[x,     y+2] = [0,255,0] 	#AdG
		#out_img[x+1,   y+2] = [0,255,0] 	#AdG
		#out_img[x-1,   y+2] = [0,255,0] 	#AdG


		return out_img


#################################################################


def plotMiddleLane(binary, middle_fitx, Minv, img_size, undistorted, ploty):
	"""Plotte Mittellinie"""

	# create new image to plot middle lane on
	warped_middle_zero = np.zeros_like(binary).astype(np.uint8)
	color_warped_middle = np.dstack((warped_middle_zero, warped_middle_zero, warped_middle_zero))

	color_warped_middle[ploty.astype('int'), middle_fitx.astype('int')] = [255,0,0]					# plot middle lane on the new image

	unwarped_middle = cv2.warpPerspective(color_warped_middle, Minv, img_size, flags=cv2.INTER_LINEAR)		# warp the middle lane back to original perspective 
   	
	if OPTIMIERUNG_EINGESCHALTET == True:										# Combine the result with the original image
		result=	color_warped_middle
	else:
		result = cv2.addWeighted(undistorted, 1, unwarped_middle, 1, 0)
			
	return result


#################################################################


def showStream(windowName, showWindow, showHelp, helpText, font, frame, undistorted, gray, warped, binary, out_img, result):
	"""Zeige aktuelles Bild im Fenster an und warte auf Tasteneingaben"""
	
	# setting up the display of the different stages of the feed as a 1x2 window
	if showWindow == 3:
		frameDisp = cv2.resize(frame, (640,480))
		undistortedDisp = cv2.resize(undistorted,(640,480))
		grayDisp = cv2.resize(gray,(640,480))
		warpedDisp = cv2.resize(warped,(640,480))
		binaryDisp = cv2.resize(binary,(640,480))
		out_imgDisp = cv2.resize(out_img,(640,480))
		resultDisp = cv2.resize(result,(640,480))
		vidBuf = np.concatenate((resultDisp, out_imgDisp), axis=1)
		
			
	# select what stage in closeup or display of all stages
	if showWindow==1: 
		displayBuf = result 
	elif showWindow == 2: 
		displayBuf = out_img
	elif showWindow == 3:
		displayBuf = vidBuf

	# show help text
	if showHelp == True:
		cv2.putText(displayBuf, helpText, (11,20), font, 1.0, (32,32,32), 4, cv2.LINE_AA)
		cv2.putText(displayBuf, helpText, (10,20), font, 1.0, (480,480,480), 1, cv2.LINE_AA)
	
	cv2.imshow(windowName,displayBuf)		#show display content in ubuntu

	key=cv2.waitKey(10)

	# check for ESC key
	if key == 27:
		print("|\n|...Programm wurde vom Benutzer beendet\n\n")
		cv2.destroyAllWindows()
		sys.exit()
	
	# check for '1' key
	elif key==49: 
		cv2.setWindowTitle(windowName,"Camera Feed")
		showWindow=1
            
	# check for '2' key
	elif key==50: 
		cv2.setWindowTitle(windowName,"lane detection")
		showWindow=2

	# check for '3' key
	elif key==51: 
		cv2.setWindowTitle(windowName,"Camera, lanes")
		showWindow=3

	# check for '4' key
	elif key==52: 
		showHelp = not showHelp
	
	if Steuerbits_16[1]==1:
		Steuerbits_16[1]=0 			# Steuerbit wieder zurueck setzen, wenn ein mal geschickt wurde			
	# check for '0' key
	elif key==48: 
		Steuerbits_16[1]=1			# autonom modus beenden	bei wert 1
		print("|...autonomer Modus vom Benutzer beendet")

	if Steuerbits_16[0]==1:
		Steuerbits_16[0]=0		
							# Steuerbit wieder zurueck setzen, wenn ein mal geschickt wurde			
	# check for '9' key
	elif key==57: 
		Steuerbits_16[0]=1			#autonom modus starten	bei wert 1
		print("|...autonomer Modus vom Benutzer gestartet")

	return showWindow



#################################################################


def extractPoint(middle_fitx,lookaheadDistance,Faktor_Meter_pro_Pixel):	
	"""Suche einen Punkt aus der Mittellinie heraus, der vom Ursprung genau die Entfernung der LookaheadDistance hat"""
	lookahead=lookaheadDistance			
	Delta_X=middle_fitx-320 				# delta from middle, length is 480(height)		
	Delta_X=Delta_X[::-1]  					# reverse the array, so that first value is at the bottom			
	Y=np.linspace(0, 479,480)		
	
	Distance=np.sqrt( (Y**2) + (Delta_X**2) )		# Betrag von unten mitte zu Punkt ueber Satz des Pythagoras a^2 +b^2 =c^2
	Sorted_Distance=np.sort(Distance)			# Betrag in aufsteigender Reihenfolge sortieren
	indices_Sorted_Distance=np.argsort(Distance)		# Indizes(Y Werte) der sortierten liste merken; ist meistens eh aufsteigend, nur wenn starke kurven drinnens sind

	for index, item in enumerate(Sorted_Distance):		# finde Index des Betrages, welches lookahead entfernt ist
		if item >=lookahead:
			index_Aimpoint_Y=index
			break
	Aimpoint_Y=indices_Sorted_Distance[index_Aimpoint_Y] 	# um tatsaechlichen y Wert von diesem Betrag zu erhalten
	#print ("index= " + str(Aimpoint_Y))	
	Aimpoint_X=Delta_X[Aimpoint_Y]

	
	DeltaX_Meter = Aimpoint_X*Faktor_Meter_pro_Pixel
	lookahead_Meter=lookahead*Faktor_Meter_pro_Pixel+0.48	#TODO anpassen, die Distanz an der die blaue linie anfaengt zum hinteren Rad
	
	Aimpoint_X_fuer_plotten=Aimpoint_X+320			# zum plotten da 320 die Mitte des Bildes ist
	
	return int(Aimpoint_X_fuer_plotten),int(Aimpoint_Y), DeltaX_Meter ,lookahead_Meter	


#################################################################



##################################################################################################################################  
#	 _    _                   _   _____                                               
#	| |  | |                 | | |  __ \                                              
#	| |__| | __ _ _   _ _ __ | |_| |__) | __ ___   __ _ _ __ __ _ _ __ ___  _ __ ___  
#	|  __  |/ _` | | | | '_ \| __|  ___/ '__/ _ \ / _` | '__/ _` | '_ ` _ \| '_ ` _ \ 
#	| |  | | (_| | |_| | |_) | |_| |   | | | (_) | (_| | | | (_| | | | | | | | | | | |
#	|_|  |_|\__,_|\__,_| .__/ \__|_|   |_|  \___/ \__, |_|  \__,_|_| |_| |_|_| |_| |_|
#	                   | |                         __/ |                              
#	                   |_|                        |___/                               
################################################################################################################################### 	
	



#################################################################
#
#		LADE PARAMETER
#
#################################################################

print("|...Lade Parameter")
# TODO Hyperparameter; bei neuer Kamera die mtx.dat und dist.dat durch distortion.py neu erzeugen
mtx = np.load("mtx.dat")					# wird benoetigt fuer Entzerrung der Linsenbeugung
dist = np.load("dist.dat")					# wird benoetigt fuer Entzerrung der Linsenbeugung

# TODO Hyperparameter; bei neuer Kamerastellung die trans_M.dat und trans_inv_M.dat durch transformation_handler.py neu erzeugen
trans_M = np.load("trans_M.dat")
Minv = np.load("trans_inv_M.dat")

Faktor_Meter_pro_Pixel=0.0022#(0.20*13)/480				#TODO anpassen, je nachdem, wie kamera steht

img_size=(640,480)
thresh_val = 230 						# Startwert fuer threshold fuer die Funktion "checkBinary" die dafuer sorgt, dass das bild aus mehr oder weniger weissen pixeln besteht
max_val = 255							# Maximalwert fuer threshold 
showWindow = 3							# Startwert fuer Fensterauswahl ueber die Tastatur
frame_number = 0						# Zaehler, um die ersten frames weg zu werfen, da sie immer schwarz sind 

init_binary_flag = True						# Muss am Anfang auf true sein
print_only_once=True
print_only_once2=True

Kamera = openCam()						# Erzeugt ein Kameraobjekt fuer gethreadeten video stream

	
histogramm_breite=int(0.12/Faktor_Meter_pro_Pixel)		# Raduis des Histogramms
histogramm_hoehe=int(0.4/Faktor_Meter_pro_Pixel)		# Hoehe des Histogramms
histogram_basis=290						# Basispunkt des Histogramms
histogram_maske = np.zeros((480,640), np.uint8)			# erzeuge leeres binary Bild
cv2.ellipse(histogram_maske, (histogram_basis,480),(histogramm_breite,histogramm_hoehe),0,0,-180,color=(255,255,255), thickness=-1) # male die Maske fuer das Histogramm in das binary	

Geschwindigkeit=10						# von 100 bis -100
Lookahead_Pixel=100
Fummelfaktor_DeltaX=1.3

if OPTIMIERUNG_EINGESCHALTET == True:				# Kein Fenster zur Anzeige erzeugen
	pass	
else:	
	windowName, showHelp, helpText, font = setupStream()	# Erzeuge Fenster zur Anzeige









#################################################################
#
#		STARTE HAUPTSCHLEIFE
#
#################################################################


print("|...Hauptschleife gestartet")
while True:							# Starte Hauptschleife

		
	start_time = time.time()
	frame = grabFrame(Kamera)			# Hole aktuellstes frame
	grab_time = time.time() - start_time
	
	#if OPTIMIERUNG_EINGESCHALTET == True:		# bei Optimierung zuerst grey, dann undistort			
	if False:	
		gray = grayFrame(frame)			
		gray_time = time.time() - grab_time - start_time
	
		undistorted = undistFrame(gray)
		undist_time = time.time()-gray_time - grab_time -start_time

		warped = warpFrame(trans_M, img_size, undistorted)
		warp_time = time.time() - gray_time - undist_time - grab_time -start_time



	else:						# Live Stream soll buntes, entzerrtes Bild sein

		undistorted = undistFrame(frame)
		undist_time = time.time() - grab_time -start_time
		
		warped = warpFrame(trans_M, img_size, undistorted)
		warp_time = time.time() - undist_time - grab_time -start_time

		gray = grayFrame(warped) #ist schon binary
		gray_time = time.time() - undist_time - grab_time -start_time -warp_time




	# aktuellen frame in puffer schreiben, da erst ueberprueft werden muss, ob er OK ist
	#binarybuffer = binaryFrame(warped, thresh_val, max_val)	
	binarybuffer=gray	
	
	# Bug, wenn aller erstes frame nicht OK ist existert noch kein binary...wird hiermit abgefangen
	if(init_binary_flag):					
		binary = binarybuffer
		init_binary_flag = False
	binary_time = time.time() - warp_time - gray_time - undist_time - grab_time -start_time
		
	# Ueberpruefen ob frame OK ist
	white_pixel_flag, thresh_val= checkBinary(binarybuffer,histogram_maske,histogramm_breite, thresh_val)
	check_binary_time = time.time() - binary_time - warp_time - gray_time - undist_time - grab_time -start_time

	if (not white_pixel_flag and print_only_once):
		print("|...Keinen akzeptablen binary Frame erhalten.\n|   Ueberspringe Berechnungen, Kontrast wird angepasst...")			
		print_only_once=False
		print_only_once2=True

	


	# Nur wenn frame dieser Iteration Ok ist; frame wird ansonsten "eingefroren" (frame von vorheriger iteration benutzen)
	if(white_pixel_flag):
			
		if print_only_once2:
			print("|...Akzeptablen binary Frame erhalten, Kontrast wurde angepasst")
			print_only_once2=False
			print_only_once=True	
			
			
		# binaeres frame aktualisieren
		binary = binarybuffer 
		if_time = time.time() - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
			
		# Erfasse Polynome der linken und rechten Ausenspur und erzeuge deren Koeffizienten
		out_img, left_fit = getPolynoms(binary,Faktor_Meter_pro_Pixel,histogram_basis,histogramm_breite,histogramm_hoehe)
		polynom_time = time.time() - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
			
		# Erzeuge x und y Werte zum Ploten der Polynome
		ploty, left_fitx, = plottablePolynoms(binary, left_fit)
		plot_value_time = time.time() - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
			
		# Berechne Mittellinie aus rechter und linker Linie
		middle_fitx = calcMiddle(binary, ploty, left_fitx, Faktor_Meter_pro_Pixel)
		middle_time = time.time() - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
			
		# Suche einen Punkt aus der Mittellinie heraus, der vom Ursprung genau die Entfernung der LookaheadDistance hat
		X_Aim, Y_Aim, DeltaX_Meter ,lookahead_Meter = extractPoint(middle_fitx,Lookahead_Pixel,Faktor_Meter_pro_Pixel) #AdG X und Y koordinate des punktes, der sich auf der lookahead distanz befindet
		extract_time = time.time() - middle_time - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
			
		# Daten an ST ueber UART schicken
		Kommunikation.sendeAnST(Geschwindigkeit,lookahead_Meter,DeltaX_Meter*Fummelfaktor_DeltaX,0,Steuerbits_16) # TODO Fummelfaktor sende Geschwindigkeit,lookahead, delta x 	
		uart_time = time.time() - extract_time	- middle_time - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time	
		

		# nichts plotten wenn Optimierung eingeschaltet ist
		if OPTIMIERUNG_EINGESCHALTET == True:	
			loop_time= time.time() -start_time		
				

			#print("grab_time :" + str(grab_time) +"\n" + "undist_time :" +str(undist_time) +"\n" + "gray_time :" + str(gray_time) +"\n" + "warp_time :" + str(warp_time) +"\n" + "binary_time :" + str(binary_time) +"\n" + "check_binary_time :" + str(check_binary_time) +"\n" + "if_time :" + str(if_time) +"\n" + "polynom_time :" + str(polynom_time) +"\n" + "plot_value_time :" + str(plot_value_time) + "\n" + "middle_time :" + str(middle_time) + "\n" + "extract_time: " + str(extract_time) + "\n" + "uart_time: " + str(uart_time)+"\nLoop_time THREADED Optimized: " + str(loop_time) +"\n\n")

	

		# Ansonsten zusaetzlich Stream anzeigen
		else:					
			#empfangen			
			#ret=Kommunikation.empfangeVonST()				# TODO aktivieren, wenn Daten vom ST empfangen werden sollen

			# Plotte Polynome und Abweichung Zielpunkt zur Mitte
			out_img = plotPolynoms(out_img, ploty, left_fitx, middle_fitx, X_Aim, Y_Aim)
			plot_time = time.time() - uart_time - extract_time- middle_time - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time	
				
			# plotte Mittellinie
			result = plotMiddleLane(binary, middle_fitx, Minv, img_size, undistorted, ploty)
			plot_middle_time = time.time() - plot_time - uart_time- extract_time	- middle_time - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time
	
			# Zeige aktuelles Bild im Fenster an und warte auf Tasteneingaben
			showWindow= showStream(windowName, showWindow, showHelp, helpText, font, frame, undistorted, gray, warped, binary, out_img, result)
			show_time = time.time() - plot_middle_time - plot_time - uart_time- extract_time - middle_time - plot_value_time - polynom_time - if_time - check_binary_time - binary_time - warp_time - gray_time - undist_time - grab_time -start_time	
		
			loop_time= time.time() -start_time		


			#print("grab_time :" + str(grab_time) +"\n" + "undist_time :" +str(undist_time) +"\n" + "gray_time :" + str(gray_time) +"\n" + "warp_time :" + str(warp_time) +"\n" + "binary_time :" + str(binary_time) +"\n" + "check_binary_time :" + str(check_binary_time) +"\n" + "if_time :" + str(if_time) +"\n" + "polynom_time :" + str(polynom_time) +"\n" + "plot_value_time :" + str(plot_value_time) + "\n" + "middle_time :" + str(middle_time) + "\n" + "extract_time: " + str(extract_time) + "\n" + "uart_time: " + str(uart_time) + "\n" + "plot_time: " + str(plot_time) +"\n" + "plot_middle_time: " + str(plot_middle_time) +"\n" + "show_time: " + str(show_time) +"\nLoop_time THREADED: " + str(loop_time) +"\n\n")

		
		

		
			



