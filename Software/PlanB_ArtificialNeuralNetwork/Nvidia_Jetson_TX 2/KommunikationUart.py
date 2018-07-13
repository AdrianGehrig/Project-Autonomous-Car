import time

import serial
import struct
from bitarray import bitarray
import cv2

class KommunikationUart:
	"""Klasse zur Kommunikation ueber UART an den ST.    Kommunkiation erfolgt ueber die Schnittstelle "/dev/ttyTHS2" und ist Stecker J17 am board"""

#############################################################################################################################################################################
#########################################################    Konfiguration    ###############################################################################################
#############################################################################################################################################################################
		
	def __init__(self):
		


          						 
#		print("|...Seriellen Port Konfigurieren")
		self.port = serial.Serial("/dev/ttyTHS2", baudrate=115200, timeout=5.0)	#Definiere den Seriellen Port "/dev/ttyTHS2" scheint der Stecker J17 zu sein
		#self.port.set_buffer_size(rx_size = 272) # entspricht 34*8, genau dem datenpaket, das wir empfangen. Somit wird verhindert, dass gepuffert wird und wenn wir lesen alte werte bekommen	
		#self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=5.0)		#fuertestzwecke in einer vm

		self.UART_Header = 0x7E7E7E7E	#Waijung erwartet ein Uart Paket mit diesem Anfang 
		self.UART_Terminator = 0x03030303	#Waijung erwartet ein Uart Paket mit diesem Ende
		
#############################################################################################################################################################################
#########################################################    SENDEN    ######################################################################################################
#############################################################################################################################################################################
	
	def sendeAnST(self,Geschwindigkeit, Lookahead,DeltaX,Soll_Stellwinkel,Steuerbits_16):
		"""Funktion zum Senden von Daten 4x floats und 16 steuerbits (ein bitarray der laenge 16)"""
	
#		print("\n|=============================| Senden Starten |==============================\n|")	
#		print("|...Sende Daten Sammeln")
		
		#DeltaX=39.123456789		# Abweichung vom Nullpunkt
		#Lookahead=0.5 			# Lookahead Distance
		#Geschwindigkeit= 42.42		# Geschwindigkeit
		#Reserve_float4=10.7 		# Reserve4 fuer Zukuenftige Variablen

	
		#Steuerbits_16=bitarray(16,endian='little')			#Steuer Bitarray erzeugen
		#Steuerbits_16.setall(False)					#alle werte auf null setzen, da sonst irgendwelche drinnen stehen...weiss gott warum



		#Steuerbits_16[0]=1		# autonomer Modus =1 
		#Steuerbits_16[1]=0		# manueller Modus =1
		#Steuerbits_16[2]=0		# Computer Vision =0 NeuralNet=1
		#Steuerbits_16[3]=0		# Reserve
		#Steuerbits_16[4]=0		# Reserve
		#Steuerbits_16[5]=0		# Reserve
		#Steuerbits_16[6]=0		# Reserve
		#Steuerbits_16[7]=1		# Reserve
		#Steuerbits_16[8]=0		# Reserve
		#Steuerbits_16[9]=0		# Reserve
		#Steuerbits_16[10]=0		# Reserve
		#Steuerbits_16[11]=0		# Reserve
		#Steuerbits_16[12]=0		# Reserve
		#Steuerbits_16[13]=0		# Reserve
		#Steuerbits_16[14]=0		# Reserve
		#Steuerbits_16[15]=0		# Reserve
		#print("|Sende Steuerbits  MUSTER: "+ str(Steuerbits_16))


		#Steuerbits_16=struct.unpack("<H", Steuerbits_16)[0] 		#bitarray wieder als unsigned short (16 bits) verpacken zum versenden
										# drecks python3... in 2.7 gings noch so	

		Steuerbits_16=struct.unpack("<h", Steuerbits_16.tobytes())[0]	# nur so funktionierts in python3
	
		#struct.unpack("<h", bytes([b, a]))[0]
		#print("|Sende Steuerbits DEZIMAL: "+ str(Steuerbits_16))


		# Alle Daten in ein Bytearray zum versenden verpacken...Header und Terminator hinzufuegen
		# Waijung erwartet einen binaeren Datenstrom, also muss das format bytearray sein. Dieser muss mit einem Header beginnen, 4 floats und ein unsignt Int32 haben.
		# das H in der struct.pack Methode bedeutet eigentlich eine short Variable (16 bit)...aber irgendwie fuellt sie automatisch alles auf 32 bit auf.
		# Deswegen muss in Waijung auch ein UINT32 erwartet werden.
		# komischerweise passieren uebertragungsfehler, wenn man eine 32 Bit Variable sendet, Waijung rundet dann irgendwie auf und es gehen bits verloren.
		# Deswegen wird nur eine 16 Bit variable gesendet.

		SendeBytearray = bytearray(struct.pack("IffffHI", self.UART_Header, Geschwindigkeit, Lookahead, DeltaX,Soll_Stellwinkel,Steuerbits_16,self.UART_Terminator))


		self.port.write(SendeBytearray)					# Auf den oben definierten seriellen Ausgangsport schreiben

#		print("|\n|==========================| Senden Abgeschlossen |===========================\n\n ")
	   						     
	   
	########################################################################################################################################################################
	#########################################################    EINLESEN    ###############################################################################################
	########################################################################################################################################################################
	
	def empfangeVonST(self):

#		print("|============================| Einlesen Starten |=============================\n|")
							
		i=0
		while i<1:									# solange wiederholen, bis etwas im Empfangspuffer angekommen ist
			
			if self.port.in_waiting: 							# nur ausfuehren wenn auch wirklich Daten im Empfangspuffer angekommen sind
													# sonst kommt es zu fehlern weil es leer ist
				


				self.port.flushInput() # ertmal angehaeuftes puffer leeren damit wir nur den aktuellsten wert bekommen


				#print("|Empfangspuffer Bytes: "+ str(port.in_waiting)) 	# Anzahl der Bytes, die im Empfangspuffer angekommen sind		
#				print("|floats: ")		
				EmpfangsBytearray = self.port.read(34) 				# 34 bytes einlesen, entspricht 8 single variablen und eine unsigned short variable, 
												# die als statusbitmuster interpretiert werden muss			
				
				EmpfangsBytearray=struct.unpack("<ffffffffH",EmpfangsBytearray) # packe die daten in eine float Liste , letztes element ist statusbitmuster
#				print("|[0]: "+ str(EmpfangsBytearray[0])) 			# druckt Inhalt der liste
#				print("|[1]: "+ str(EmpfangsBytearray[1])) 
#				print("|[2]: "+ str(EmpfangsBytearray[2]))
#				print("|[3]: "+ str(EmpfangsBytearray[3])) 
#				print("|[4]: "+ str(EmpfangsBytearray[4])) 
#				print("|[5]: "+ str(EmpfangsBytearray[5])) 
#				print("|[6]: "+ str(EmpfangsBytearray[6]))
#				print("|[7]: "+ str(EmpfangsBytearray[7]))
#				print("|")
				#print("|Statusbits: "+ str(EmpfangsBytearray[8]))		# statusbits als int
					
		
				Statusbits=bitarray("{0:b}".format(EmpfangsBytearray[8]))	# Intiger zu binaerern zahl formatieren.Diese binaere Zahl in bitarray schreiben
				#print("|Laenge: "+ str(len(Statusbits)))		
				if len(Statusbits)<16:						# wenn bitmuster, das ankommt kleiner als 16 ist dann mit nullen auffuellen
					b=bitarray(16-len(Statusbits))				# erzeuge ein Bitarray, der laenge der fehlenden nullen
					b.setall(False)						# alle werte auf null setzen, da sonst irgendwelche drinnen stehen...weiss gott warum
					Statusbits=Statusbits[::-1]				# wegen little und big endian format...dreht die liste ein mal um
					Statusbits.extend(b)					# erst jetzt die nullen am ende hinzufuegen
				
				else:
					Statusbits=Statusbits[::-1]				# wegen little und big endian format...dreht die liste ein mal um
	
	
				
#				print("|Statusbitmuster: "+ str(Statusbits))	#statusbitmuster
#	
#				print("|[ 0]: "+ str(Statusbits[0])) 	# autonomer Modus =1 manueller Modus =0
#				print("|[ 1]: "+ str(Statusbits[1]))	# Reserve
#				print("|[ 2]: "+ str(Statusbits[2]))	# Reserve
#				print("|[ 3]: "+ str(Statusbits[3])) 	# Reserve
#				print("|[ 4]: "+ str(Statusbits[4])) 	# Reserve
#				print("|[ 5]: "+ str(Statusbits[5])) 	# Reserve
#				print("|[ 6]: "+ str(Statusbits[6]))	# Reserve
#				print("|[ 7]: "+ str(Statusbits[7]))	# Reserve
#				print("|[ 8]: "+ str(Statusbits[8]))	# Reserve
#				print("|[ 9]: "+ str(Statusbits[9])) 	# Reserve	
#				print("|[10]: "+ str(Statusbits[10]))	# Reserve 
#				print("|[11]: "+ str(Statusbits[11]))	# Reserve
#				print("|[12]: "+ str(Statusbits[12]))	# Reserve 
#				print("|[13]: "+ str(Statusbits[13]))	# Reserve 
#				print("|[14]: "+ str(Statusbits[14]))	# Reserve 
#				print("|[15]: "+ str(Statusbits[15])+"\n")	# Reserve
	
	
				i=1	#es wurde etwas eingelesen, also schleife beenden
				
		#self.port.close() #port schliessen , sonst bleibt er offen und keine andere Anwendung kann ihn benutzen
		
		
		#Dictionarry zurueckgeben, in dem alle werte drinnen stehen und einen Namen haben		
		return {'MomentanGeschwindigkeit':EmpfangsBytearray[0],'ProzentGaspedal':EmpfangsBytearray[1],'aktuellerStellwinkel':EmpfangsBytearray[2],'ReserveFloat4':EmpfangsBytearray[3],'ReserveFloat5':EmpfangsBytearray[4],'ReserveFloat6':EmpfangsBytearray[5],'ReserveFloat7':EmpfangsBytearray[6],'ReserveFloat8':EmpfangsBytearray[8],'Bit_Modus_manuell_oder_autonom':Statusbits[0],'StatusReserve2':Statusbits[1],'StatusReserve3':Statusbits[2],'StatusReserve4':Statusbits[3],'StatusReserve5':Statusbits[4],'StatusReserve6':Statusbits[5],'StatusReserve7':Statusbits[6],'StatusReserve8':Statusbits[7],'StatusReserve9':Statusbits[8],'StatusReserve10':Statusbits[9],'StatusReserve11':Statusbits[10],'StatusReserve12':Statusbits[11],'StatusReserve13':Statusbits[12],'StatusReserve14':Statusbits[13],'StatusReserve15':Statusbits[14],'StatusReserve16':Statusbits[15]}

#		print("|\n|==========================| Einlesen Abgeschlossen |========================= ")
	   						       














#Kommunikationsobjekt erzeugen
#com=KommunikationUart()

#steuerbits setzen
#Steuerbits_16=bitarray(16,endian='little')			#Steuer Bitarray erzeugen
#Steuerbits_16.setall(False)					#alle werte auf null setzen, da sonst irgendwelche drinnen stehen...weiss gott warum
#Steuerbits_16[0]=0
#Steuerbits_16[1]=0

#rueber schicken
#com.sendeAnST(10,0,0,0,Steuerbits_16)

#warten auf empfangsdaten
#ret=com.empfangeVonST()

#Teile des empfangenen Dictionarrys ausdrucken
#print(ret['StatusReserve1'] , ret['StatusReserve2'],ret['StatusReserve3'],ret['StatusReserve4'],ret['StatusReserve8'],ret['StatusReserve9'],ret['StatusReserve13'],ret['StatusReserve16'])















