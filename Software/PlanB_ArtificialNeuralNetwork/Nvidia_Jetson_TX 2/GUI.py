from appJar import gui

import _thread
#import driveGUI
from driveGUI import calc_steering,reset_stop_flag,set_stop_flag,set_autonomer_modus,set_manueller_modus,lese_von_ST,set_Gaspedal_Stellung,show_Frame
app = gui("control panel","550x550")


Start=False
dir_path="Noch kein Model ausgewählt"


##################################################################################################
############  Funktionen die bei anklicken der Buttons aktiviert werden ##########################
##################################################################################################

def pressSelectModel(button):
	
	global Puffer_dir_path
	global dir_path


	print("|...Neuen Model Ladeort setzen")	
	Puffer_dir_path=app.openBox(title="model file", dirName=None, parent=None)



	if (str(Puffer_dir_path) == "None") or(str(Puffer_dir_path) =="()") or(str(Puffer_dir_path) ==""):		#wenn man das[x] anklickt oder [cancel]
		print("|...	abgebrochen")	
	
	else:
		dir_path=Puffer_dir_path						# Wenn ein gültige Pfad angegeben wurde die globale Variable überschreiben
		print("|...	Neuer Ladeort: "+ str(dir_path))
		app.setLabel("SaveDirectory", dir_path)

	
##################################################################################################


def pressStart(button):
	global Start	
	global dir_path



	if not Start:									# nur ausführen, wenn zum ersten mal start gedrückt wurde
		
			
		if not str(dir_path) ==  'Noch kein Model ausgewählt':		# nur ausführen, wenn es einen gültigen pfad gibt

			print("|\n|\n|\n|...LADE Model: "+ str(dir_path))
			reset_stop_flag()
			_thread.start_new_thread( calc_steering, (dir_path,) )
			app.setButton("Start Model", "Stop Model")
			Start=True
			app.setButtonBg("Start Model", "LimeGreen")
		else:
			print ("|...Es wurde kein gültiger Pfad angeben")
			app.errorBox("Obacht, kein gültiger Pfad", "\nEs wurde noch kein Model ausgewählt.\n\nMit dem Button [Select Model] muss erst noch eine model.h5 Datei ausgewählt werden ", parent=None)




	else:										# Wenn schon mal Start gedrückt wurde Button Text invertieren und Thread stoppen
		set_stop_flag()		
		app.setButton("Start Model", "Start Model")
		Start=False
		print("|...Model gestoppt"+ str(Puffer_dir_path))
		app.setButtonBg("Start Model", "LightCoral")

##################################################################################################


def pressModus(button):
	if not Status: #wenn manueller modus
		set_autonomer_modus()
	else:
		set_manueller_modus()

##################################################################################################

def pressGaspedal(button):
	set_Gaspedal_Stellung(app.getScale("Gaspedal"))


##################################################################################################
############  Seperate Funktionen  ###############################################################
##################################################################################################

def aktualisiere_Gui_mit_Daten_von_ST():
	global Status
	while True:	
		UartEmpfang=lese_von_ST()
		Status=UartEmpfang['Bit_Modus_manuell_oder_autonom']
		if Status:
			app.setButtonBg("Modus", "LimeGreen")
			app.setButton("Modus", "Stoppe autonomen Modus")
		if not Status:
			app.setButtonBg("Modus", "LightCoral")
			app.setButton("Modus", "Starte autonomen Modus")





##################################################################################################
############  Gui Layout erzeugen ################################################################
##################################################################################################

## Zeige Pfad zu aktuellem Model an
app.addLabel("SaveDirectory",dir_path,0,0,6)
app.getLabelWidget("SaveDirectory").config(font="Helvetica 10")
app.setLabelBg("SaveDirectory", "DarkGray")


## Button zum auswählen eines Modells
app.addButtons(["SelectModel"], pressSelectModel,1,0,0)
app.getButtonWidget("SelectModel").config(font="Helvetica 12")

## Button zum Starten eines Modells
app.addButtons(["Start Model"], pressStart,1,1,0)
app.getButtonWidget("Start Model").config(font="Helvetica 12")
app.setButtonBg("Start Model", "LightCoral")


## Slider zum steuern der Geschwindigkeit

app.addScale("Gaspedal")
app.setScale("Gaspedal", 10, callFunction=True)
app.setScaleChangeFunction("Gaspedal", pressGaspedal)
app.setScaleRange("Gaspedal" ,0, 100, curr=12)
app.showScaleValue("Gaspedal", show=True)
app.getScale("Gaspedal")
app.showScaleIntervals("Gaspedal", 25)

## Button zum Starten des autonomen Modus
app.addButtons(["Modus"], pressModus,2,1,0)
app.getButtonWidget("Modus").config(font="Helvetica 12")
app.setButton("Modus", "Starte autonomen Modus")
app.setButtonBg("Modus", "LightCoral")









#_thread.start_new_thread( show_Frame, () ) # auf seperaten Thread das aktuelle input Bild ins netz zeigen... muss aber parallel zur Hauptschleife in der driveGUI.py laufen, sonst wird die Hauptschleife langsamer


_thread.start_new_thread( aktualisiere_Gui_mit_Daten_von_ST, () ) #soll parallel immer laufen und Gui aktualisieren



app.go()
