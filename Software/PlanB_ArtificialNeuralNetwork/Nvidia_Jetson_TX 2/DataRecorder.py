
print("\n\n|...DataRecorder gestartet")    
import time
import _thread

# import GUI
from appJar import gui


#imports Kamera
print("|...suche Kamera") 
import cv2
from imutils.video import WebcamVideoStream				
import imutils	
Kamera = WebcamVideoStream(src="/dev/video1").start()
frameCounter=0

import os 
# Suche nach schon bestehender csv datei
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_pathF =dir_path+"/Features/"
if os.path.isfile(dir_pathF + "FahrtLog.csv"):
	ExistsFahrtLog=True
else:
	ExistsFahrtLog=False

# erzeuge default save folder, wenn nicht existiert

#dir_path = os.path.dirname(os.path.realpath(__file__))
dir_pathFI =dir_pathF+"IMG/"
if not os.path.exists(dir_pathFI):
	print("|...Kein default Save Ordner gefunden, erzeuge neuen")    
	os.makedirs(dir_pathFI)




print (dir_pathFI)


# erzeuge leere Log Datei
import csv
#with open('FahrtLog.csv', 'w', newline='') as csvfile:
#	Logger = csv.writer(csvfile, delimiter=' ',quotechar=',', quoting=csv.QUOTE_MINIMAL)
	


# Bereite Uart Kommunikation vor
print("|...Seriellen Port Konfigurieren")
from bitarray import bitarray					# Bitarray fuer Steuerbits
import KommunikationUart as MyModule				# Klasse fuer UART Kommunikation
Kommunikation=MyModule.KommunikationUart() 			# Objekt der Klasse KommunikationUart Erzeugen

Steuerbits_16=bitarray(16,endian='little')			# Steuer Bitarray erzeugen
Steuerbits_16.setall(False)					# Alle Werte auf null setzen, da sonst zufaellige drinnen stehen



# Status ob pausiert oder gestoppt wird muss am anfang fasle sein

Pause=False
Stop=False
	
##################################################################################################
############  Funktionen die bei anklicken der Buttons aktiviert werden ##########################
##################################################################################################

def pressRecordFunction(button):
	global Pause
	global Stop
	global frameCounter
	global ExistsFahrtLog
	global dir_path
	global dir_pathF

	
	if button == "Start":
	        #app.stop()
		global FPS
		
		## ueberpruefen, ob fahrtlog schon existert, wenn ja dann zaehler hoch setzen

		if (ExistsFahrtLog) and (not Pause):
			print("exists and not pause")			

			with open(str(dir_pathF) +"/FahrtLog.csv", 'rb') as existcsvfile:
				row_count = sum(1 for row in existcsvfile)  # fileObject is your csv.reader
				print("|... Datensätze gefunden : " + str(row_count))
				

			DatenAnhaengen=app.okBox("Obacht Datei existiert schon", "Im angegebenen Pfad existert schon eine FahrtLog.csv\n\n"+ str(row_count) +" Datensätze wurden gefunden, soll dieser Datensatz erweitert werden?", parent=None)	

			if not DatenAnhaengen:
				return  # stoppen, wenn cancel geklickt wurde
		
		# wenn OK gedrueckt wurde frame Counter anpassen		
			if DatenAnhaengen:
				frameCounter=row_count
				
		
		app.setLabel("Status", "Aufnahme läuft")
		app.setLabelBg("Status", "LightCoral")
		app.setLabelBg("DatensatzCounter", "LightCoral")			
		app.disableButton("Start")
		app.enableButton("Pause")
		app.enableButton("Stop")
		FPS = app.getSpinBox("FPS")
		

		if not Pause:	
			_thread.start_new_thread( captureFrames,() )
			print ("|...Aufnahmethread gestartet")
		else:
			print ("|...Aufnahme geht weiter ")
		Stop=False
		Pause=False
	
	elif button == "Pause":
	     	#usr = app.getEntry("Username")
	      	#pwd = app.getEntry("Password")
		#print("User:", usr, "Pass:", pwd)
		app.setLabel("Status", "Aufnahme pausiert")
		app.setLabelBg("Status", "LimeGreen")
		app.setLabelBg("DatensatzCounter", "LimeGreen")
		app.disableButton("Pause")
		app.enableButton("Start")		
		app.setLabel("DatensatzCounter", "Datensätze: "+ str(frameCounter))
		Pause=True
		print("|...Aufnahme pausiert. Datensätze: "+str(frameCounter))
			

	elif button == "Stop":
		
		app.setLabel("Status", "Aufnahme gestoppt")
		app.setLabelBg("Status", "LightGray")
		app.setLabelBg("DatensatzCounter", "LightGray")
		app.disableButton("Stop")
		app.disableButton("Pause")
		app.enableButton("Start")
	


		Pause=False
		Stop=True
		print("|...Aufnahme gestoppt. Datensätze: "+str(frameCounter))		
		
		


##################################################################################################


def pressChangeDirectoryFunction(button):				#TODO checken ob csv schon da is
	print("|...Neuen Speicherort setzen")	
	global dir_path
	global dir_pathF
	global dir_pathFI		
	global ExistsFahrtLog
	Puffer_dir_path=app.directoryBox(title="SaveFeatures", dirName=None, parent=None)
	
	if (str(Puffer_dir_path) == "None") or(str(Puffer_dir_path) =="()"):		#wenn man das[x] anklickt
					
			print("|...	abgebrochen")
			pass
			
	
	else:
		

		

		dir_path=Puffer_dir_path
		dir_pathF=dir_path+"/Features/"
		dir_pathFI=dir_pathF+"IMG/"	
		
		
		#dir_path +="/Features/"
		# Suche nach schon bestehender csv datei
		#dir_path = os.path.dirname(os.path.realpath(__file__))

		if os.path.isfile(dir_pathF + "FahrtLog.csv"):
			ExistsFahrtLog=True
		else:
			ExistsFahrtLog=False

		# erzeuge default save folder, wenn nicht existiert

		#dir_path = os.path.dirname(os.path.realpath(__file__))
		
		if not os.path.exists(dir_pathF):
			print("|...Kein default Save Ordner gefunden, erzeuge neuen")    
			os.makedirs(dir_pathFI)

		
		app.setLabel("SaveDirectory",dir_path)
		print("|...	Neuer Speicherort: "+ str(dir_path))

		pass



##################################################################################################
############  Seperate Funktionen  ###############################################################
##################################################################################################



def captureFrames():
	global frameCounter	
	global dir_path
	global dir_pathFI
	global ExistsFahrtLog
	#global Pause
	#global Stop
	#global FPS #nicht noetig, globale variablen muessen nur ein mal definiert werden
	
	print("|...Starte Aufnahme mit " + FPS +" Fps")	
	delayTime=1.0/float(FPS)
	
	# Erzeuge leere csv Datei und schreibe daten da rein	
	#with open('Features/FahrtLog.csv', 'w', newline='') as csvfile:
	with open(str(dir_pathF) +"/FahrtLog.csv", 'a', newline='') as csvfile:	
		Logger = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		ExistsFahrtLog=True # damit oben gecheckt werden kann ob die datei schon da ist, dass man sachen anhaengen kann
		
		timerbuffer=time.time()
		while True:
			if (not Pause) and (not Stop):		
								
				frameCounter+=1			
				frame = Kamera.read()								# Frame grabben
				
				EmpfangVonST=Kommunikation.empfangeVonST()					# Uart Daten einlesen
					
				frame=cv2.resize(frame, (320,240))
				framePathAndName=str(dir_pathFI)+"frame"+ str(frameCounter) +".jpg"
				
				cv2.imwrite(framePathAndName, frame)
				
				ProzentGaspedal=EmpfangVonST['ProzentGaspedal']
				#print(ProzentGaspedal)				
				
				aktuellerStellwinkell=EmpfangVonST['aktuellerStellwinkel']
				#print(aktuellerStellwinkell)	


				# schreibe in Log datei: Pfad der datei, Stellwinkel, Gaspedalstellung, zeitdifferenz zu letzter Aufnahme
				Logger.writerow([framePathAndName,aktuellerStellwinkell,ProzentGaspedal, time.time()-timerbuffer])
				
				timerbuffer=time.time()
				
				if frameCounter % 10 ==0: # Modolo nur wenn der Counter um 10 hoeher ist updaten	
					app.setLabel("DatensatzCounter", "Datensätze: "+ str(frameCounter))	
				time.sleep(delayTime)	

	
			if Stop:
				frameCounter=0
				app.setLabel("DatensatzCounter", "Datensätze: "+ str(frameCounter))					
				print("|...Aufnahme Thread beendet")
				return






##################################################################################################
############  Gui Layout erzeugen ################################################################
##################################################################################################

print("|...Erzeuge GUI") 

# create a GUI variable called app
app = gui("Adrians toller Datenrekorder", "550x270")
#app.setPadding([20,0]) # 20 pixels padding outside the widget [X, Y]
app.setStretch("both")
app.setSticky("nesw")

app.setBg("LightGray")
app.setFont(18)

# add & configure widgets - widgets get a name, to help referencing them later



app.addLabel("SaveDirectory",dir_path,0,0,6)
app.getLabelWidget("SaveDirectory").config(font="Helvetica 12")
app.setLabelBg("SaveDirectory", "DarkGray")
app.addButtons(["Change"], pressChangeDirectoryFunction,0,6,1)
app.getButtonWidget("Change").config(font="Helvetica 12")


#app.addLabelEntry("Fps")



# link the buttons to the function called press

app.addSpinBoxRange("FPS", 1,30,1,0,6).config(font="Helvetica 12")
app.setSpinBox("FPS", 7, callFunction=True)


#app.addLabelEntry("FPS",1,0,1)
app.addLabel("TextFPS", "Fps",1,6,1)
app.getLabelWidget("TextFPS").config(font="Helvetica 12")


app.addHorizontalSeparator(2,0,7, colour="LightGray")
app.addButtons(["Start", "Pause","Stop"], pressRecordFunction,3,0,7)


app.addHorizontalSeparator(4,0,7, colour="LightGray")

app.addLabel("Status", "Ausgeschaltet",5,0,7)
app.addLabel("DatensatzCounter", "Datensätze: "+ str(frameCounter),6,0,7)

app.addHorizontalSeparator(7,0,7, colour="LightGray")

app.disableButton("Pause")
app.disableButton("Stop")




# start the GUI
app.go()




	





