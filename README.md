# Project Autonomous Car
_This is a student project. Two other students and me built and wrote software for a self driving rc car._
[Thumbnail]: https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/Auto_auf_Strecke.PNG "Thumbnail"

Schematic overview:
[electrical_concept]: https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/%C3%9Cbersicht.pdf "electrical_concept"



## Plan A,  (Computer Vision)
[CVgood]: https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_ideal2.png"CVgood"
* The Idea:
1. warp perspective into bird's-eye view
2. convert to binary image
3. search for ones from top to bottom, with a moving window approach
4. calculate a 2. order polynom through the left line and add an offset to calculate the ideal middle lane
5. calculate the steering angle, so that the wheels hit a defined point on the ideal middle lane
6. save the beginning of the middle lane for the next frame. The moving windows will start to search here. 
This allows tracking of the middle lane, if it wanders over the time.

* Where we failed:
Unpredictable white sun reflections on the course, that swallowed the white lane markings. 
Even with a lot of optimisation the information loss was too big to work properly with Plan A.
[CVfails]: https://github.com/AdrianGehrig/Project-Autonomous-Car/blob/master/Documentation/OpenCV_Spiegelung.png"CVfails"




## Plan B,  (Artificial Neural Net)
_This approach is heavily inspired by:_ 
* _["How to Simulate a Self-Driving Car
" from Siraj Raval]()_
* _["End to End Learning for Self-Driving Cars" NVIDIA from NVIDIA](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf)_
