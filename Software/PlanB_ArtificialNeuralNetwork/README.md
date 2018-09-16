# Plan B - Getting Started

_This is a quick startup guide for Plan B, the Artificial Neural Network Approach._

1. NVIDIA Jetson

   _Used for Image Processing and Calculating of the steering angle._
   
2. STM32 F4 Part (Identical in PlanA and PlanB)

   _Used for Hardware communication and basic safety features._




___
<br><br>

# 1. NVIDIA Jetson Part

### WARNINGS:
* **ALWAYS** connect the Low Voltage Buzzer to the lipo, **while driving** to get audio feedback, when to change the lipos
* **ALWAYS** disconnect the Lipo after you're **done driving** the car. Also disconnect the Low Voltage Buzzer as it consumes energy aswell. Otherwise the lipo will be discharged for days. If the Lipo is deeply discharged, it will get puffy and damaged permanently. If the lipo is visibly swollen, you should not charge it anymore! 
* **ALWAYS** keep the transmitter in your hands, to disable the autonomous mode at any moment. By touching the steering wheel or the accellerator, the car will initiate an emergency break for one second. After this break the car returns to manual mode.


## 1.1 Normal starting procedure
_If nothing has changed and the current state is still as we left it in SS18 this will work:_

_If you want to start driving right away, without recording a dataset and training a model, start this list at point 15_

_If you want to start with recording a new Dataset, start this list at point 1._



1. Setup a test environment an get ready to drive the car manually via the remote control as perfect as possible.

2. Boot the Jetson [Red Power Button] and login with Username: Nvidia, PW: nvidia
3. Open the explorer and navigate into the "PlanB" directory. All the files listed in the GitHub subfolder "PlanB_ArtificialNeuralNetwork" should still be on the Jetson. If not, download them from this GitHub repository.
4. Open a Command promt window by right clicking and selecting "start command window here" in the explorer.

5. Type in **python3 datarecorder.py** and hit enter...the recorder GUI should start.
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Datenrecorder.png)

6. Click [change], to change the folder, where the dataset will be recorded to. The current path is shown on the left.
7. Get ready, to drive the car and click [Start]. If the program detects an existing dataset in the selected path, it asks you, if you want to extend or overwrite this existing dataset. Recording of frames and associated steering angle and accelerator data from the remote controller will start.
8. Press [Pause], if you want to pause your recordings, in order to record another scenario. Hit [Start] again to continue.
9. Press [Stop] to stop your recordings.
10. A Dataset was created and the model of the artificial neural net can now be trained on it. Open **model.py** and play around with the Hyperparameters in the ArgumentParser, e.g. 'number of epochs' or 'learning rate'.
11. Start the training procedure by calling the following command: "python3 model.py dataset2" ...where "dataset2" is the folder name, where the dataset has been recorded to. This training may take some hours/days according to your settings in **model.py**. Training in the would be more time efficient, but we never tried it.
12. When training is done and everything went successfully, there should be some new files in the current directory. Those are the trained models and some logging files. The file with the highest number is the best trained model. Cut those files and paste them into a new subfolder under e.g. "dataset2".  
13. Save a new file called "info" in that subfolder and write down, what settings you have made in **model.py** for this training session.
14. Show the learning results by opening **plot_history.py**, change the "path" variable at line 4 to the path, where you've pasted the new files above.
  Save and run **plot_history.py**. the logging files are visualized and saved as .png in the subfolder for you for further inspection.   The aim is to get the "test" loss as low as possible. It should look something like this:
  
  ![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/HistoryLossFigure.png)

15. Type in **python3 GUI.py** and hit enter
  ...the GUI for selecting and running a trained model should start.
   ![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Control%20panel.PNG) 
16.  Klick (1) [SelectModel] and browse to the trained model file, you want to deploy. The selected model path will be displayed in the GUI afterwards (2).
17. Klick [Start Model] (3)
   
   If the console shows some kind of "streamer Error" you need to unplug and replug the USB camera.
   
   If tensorflow throws errors "...could not allocate...." restart the process
   
   If everything goes right "Feuer frei! -->" will be displayed in the console.
   
18. Adjust the speed in percentage with the slider (4)
19. Start the autonomous mode by klicking (5) [Starte autonomen Modus] The button will turn green, if everything went right and the car will start driving by it self.
20. If the button is pressed again or if the steering wheel or the accellerator on the remote control is touched, the car will initiate an emergency break for one second. After this break the car returns to manual mode.



42. Have fun!

## 1.2 Overview of the files


# TODO
___
<br><br>

# 2. STM32 F4 Part (Identical in PlanA and PlanB)
The microcontroller is programmed in Simulink. The C code for the microcontroller is generated and downloaded with the click of a button! Waijung is a very handy library, that has some prebuilt blocks for acessing the microcontrollers hardware. E.g. a block for sending PWM signals or communicating via UART. 

For further instructions on istallation, Getting Started, Tips and Tricks please read:

["Matlab zu Discovery Board.docx" in the documentation path](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Matlab%20zu%20Discovery%20Board.docx "Word Document")

## 2.1 Overview
After correctly installed the drivers and the Waijung package, open **STDiscovery2016a.slx** in Simulink.

Simulink is a graphical programming lauguage, individual program parts can be organized in subsystems. Waijung blocks for reading data are located on the left side. For processing the data, the infromation is carried via black arrows from one block to another. Logical or calculating operations are done in the middle section. Finally the Waijung output blocks are located on the right side.

![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Waijung%20overview.PNG)



### (1) Global Variables
They are read/writable in every subsystem underneath. They are used multiple times and some will be predifined once in **(6).**

An alternative way would be to run a matlab script in **(6)** , were all the variables would be declaired and some predefined.

### (6) Initialisation
Some global Variables are predefined here

### (2) Waijung Initialisation Block
This block needs to be in the top layer, when Waijung blocks are used

### (3) Reading actual velocity
A hall sensor is processed here and the velocity is calculated. This variable will be sent back to the Jetson, and displayed in the GUI

### (4) Actuators
motor and servo logic is located in this subsystem. Also the safety feature for disabling the autonomous mode, when touching the steering wheel or the accelerator on the Transmitter is found here.

At the moment two bits are send to the STM32F4 over UART, "Computer Vision Mode" and "Neural Net Mode". These bits enable or disable a certain feature in the Simulink Program...This can be confusing. In a future version, the microcontroller should only get a single steering and velocity command over UART (2x float) for better readability.

### (5) Communication
The Data, that is read in via the Waijung UART blocks will be wirtten to global receiving variables.
The global sending variables will be send via the Waijung UART blocks to the Jetson. 

### (7) Status LEDs
The Status LED pattern for the autonomous and manual mode is generated here.

### (8) Power Distribution Unit
Not implemented yet. The idea was to read the current consumption of some FETs an disable them, if the consumption reaches a certain limit

### (9) Debug
This subsystem is used when debugging the microcontroller over an FDTI connection. An FDTI Adapter or an Arduino (["as seen here on ther very bottom here"](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Matlab%20zu%20Discovery%20Board.docx "Word Document")) can be used for that.
Some Varaibles can be sent back for debugging to a PC. Or an event can be triggered, when sending a certain Ascii caracter from the PC to the STM32F4.


### (10) Build Model
Connect the Microcontroller to the PC via USB.
Press this button to compile the the Simulink program to C code and download it to the STM32F4.

## 2.2 Some hints
* Do not use "äöü" or any fancy symbols underneath Waijung blocks...the compiler just throws a cryptic error message and won't compile
* Do not use hardware ports multiple times in Waijung blocks, always keep an eye on your used ports, like(["this visio drawing"](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/ST_Pinout_und_Anschl%C3%BCsse.pdf))
* Some ports are selectable in Waijung for certain features, but the hardware does not support it. The compiler just won't compile, but the error message is misleading and cryptic.


