# Plan A - Getting Started

_This is a quick startup guide for Plan A, the Computer Vision Approach._

1. NVIDIA Jetson

   _Used for Image Processing and Calculating of the steering angle._
   
2. STM32 F4 Part (Identical in PlanA and PlanB)

   _Used for Hardware communication and basic safety features._



___
<br><br>

# 1. NVIDIA Jetson Part
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_ideal2.png "CVgood")
### WARNINGS:
* ALWAYS connect the Low Voltage Buzzer to the lipo, **while driving** to get audio feedback, when to change the lipos
* ALWAYS disconnect the Lipo after you're **done driving** the car. Also disconnect the Low Voltage Buzzer as it consumes energy aswell. Otherwise the lipo will be discharged for days. If the Lipo is deeply discharged, it will get puffy and damaged permanently. If the lipo is visibly swollen, you should not charge it anymore! 
* ALWAYS keep the transmitter in your hands, to disable the autonomous mode at any moment. By touching the steering wheel or the accellerator, the car will initiate an emergency break for one second. After this break the car returns to manual mode.


## 1.1 Normal starting procedure
_If nothing has changed and the current

1. Boot the Jetson [Red Power Button] and login with Username: Nvidia, PW: nvidia
2. Open the explorer and navigate into the "PlanA" directory. All the files, listed in the GitHub subfolder "PlanA_ComputerVision" should still be on the Jetson. If not download them from this GitHub repository.
3. Open a Command promt window by right klicking and selecting "start command window here" in the explorer.
4. Type in **python main.py** and hit enter...the GUI should start.

   If the console shows some kind of "streamer Error" you need to unplug and replug the USB camera.


   If the GUI doesn't show up, open the main.py file in the editor and search for "OPTIMIERUNG_EINGESCHALTET = True"
set it to "OPTIMIERUNG_EINGESCHALTET = False" , save the file and retry.

5. Start the autonomous mode by pressing [9] on the keyboard (Even works though SSH connection) or the blue button on the STM32F4 Board, located on the back of the car.
6. Leave the autonomous mode by pressing pressing [9] on the keyboard or by touching the steering wheel or the accellerator on the transmitter.


# 2. STM32 F4 Part (Identical in PlanA and PlanB)

