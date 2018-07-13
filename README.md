# Project Autonomous Car
_This is a student project. Two other students and I built and wrote software for a self-driving rc car._
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Auto_auf_Strecke.PNG "Thumbnail")

### Schematic overview:
![alt](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/%C3%9Cbersicht.jpg)

___
<br><br>
## Plan A,  Computer Vision
### Concept:
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_ideal2.png "CVgood")

1. Warp perspective into bird's-eye view
2. Convert to binary image
3. Search for ones from top to bottom, with a moving window approach
4. Calculate a 2. order polynomic through the left line and add an offset to calculate the ideal middle lane
5. Calculate the steering angle, so that the wheels hit a defined point on the ideal middle lane
6. Save the beginning of the middle lane for the next frame. The moving windows will start to search here. 
This allows tracking of the middle lane if it wanders over the time.

### Where we failed:
Unpredictable white sun reflections on the course, that swallowed the white lane markings. 
Even with a lot of optimization the information loss was too big to work properly with Plan A.
![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_Spiegelung.png "CVfails")
### Conclusion Plan A:
Classic computer vision is strong, when it comes to debugging. The whole process follows a strict known algorithm that can be tweaked precisely. However, this approach lacks, when it comes to abstraction. If the input lacks in information or is slightly different the program fails.

___
<br><br>

## Plan B,  Artificial Neural Net
_This Behavioral Cloning is heavily inspired by:_ 
* _["How to Simulate a Self-Driving Car
" from Siraj Raval]()_
* _["End to End Learning for Self-Driving Cars" NVIDIA from NVIDIA](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf)_
### Concept:

1. Let a human drive the rc car on the course multiple times as good as he can under different conditions.
* harsh light conditions, dark and bright
* cover parts of the track randomly or adding "noise" 
* take the track to different environments, to change the surrounding

2. Record frames meanwhile from the camera, save the corresponding steering angle and speed from the human driver to a csv file
3. Train the model from NVIDIA to learn what kind of picture leads to which steering angle
4. Deploy the trained model on the physical car




### Conclusion Plan B
The main key to success is DATA! A diverse training dataset leads to a more stable driving behavior. 
The best result was achieved with the dataset consisting of 80% driving in the middle of the right lane and 20% returning from outside of the track or the wrong lane into the correct right lane. 
Plan B is more kind of a "black box “, when it comes to debugging. Because a wrong driving behavior can't be traced back to a specific line of code in the trained model.
However, this approach is vastly superior than Plan A when it comes to the random sun reflections and noise. Even if the lane markings are just barely visible the car manages it to stay in the correct lane surprisingly well.

![alt text](https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/InAction.mp4
"Video")
