# Plan A - Getting Started

_This is a quick startup guide for Plan A, the Computer Vision Approach._

1. NVIDIA Jetson

   Used for Image Processing and Calculating of the steering angle.

2. STM32 F4 Part (Identical in PlanA and PlanB)

  Used for Hardware communication and basic safety features.



___
<br><br>

## 1. NVIDIA Jetson Part
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_ideal2.png "CVgood")
### WARNINGS:
* ALWAYS connect the Low Voltage Buzzer to the lipo, **while driving** to get audio feedback, when to change the lipos
* ALWAYS disconnect the Lipo after you're **done driving** the car. Also disconnect the Low Voltage Buzzer as it consumes energy aswell. Otherwise the lipo will be discharged for days. If the Lipo is deeply discharged, it will get puffy and damaged permanently. If the lipo is visibly swollen, you should not charge it anymore! 
* ALWAYS keep the transmitter in your hands, to disable the autonomous mode at any moment. By touching the steering wheel or the accellerator, the car will initiate an emergency break for one second. After this break the car returns to manual mode.






## 2. STM32 F4 Part (Identical in PlanA and PlanB)

