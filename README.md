# Grand Theft Auto San Andreas Autonomous Driving
Autonomous driving in the game "Grand Theft Auto San Andreas".


# Summary
An autonomous driving system for "Grand Theft Auto San Andreas" video game. <br>
Models analyse the game screen and predict the best move for that time. <br>
There is a model using pure image processing and another model using CNN deep learning architecture to decide what to do in every frame. <br>


# Models
There are two autonomous driving car models. <br>
* First one is a simple car that is detecting two road lanes and decide what to do according to them. <br>
* Second model is based on a **CNN** deep learning model.

## Simple Car model
It is based on road lanes and makes decisions by looking at road lanes. <br>
Not AI based.

## CNN model
This model is a Convolutional Neural Network model written in Keras. It consists of a few convolutional blocks and a fully connected block. 
You can see the architecture of the model [here](https://github.com/yigitatesh/gta_san_andreas_autonomous_driving/blob/main/img/model_architecture.png). <br>

The program takes a screenshot of the game window and predicts the best move for that time according to the predictions of the CNN model. <br>


# Data
Images and corresponding moves per images are collected by a real user while he is playing the video game. <br>
Roughly 75.000 image-move pairs are collected. Images have been saved with 60x60 sizes and in grayscale format to save disk storage. <br>


# Requirements
## For Simple Car model (simple_car.py)
- opencv
- mss
- win32api
## For CNN Model (run_model.py)
- tensorflow-gpu
- cuda and cudnn support
- opencv
- mss
- win32api


# How to Run

## Simple car model
Run simple_car.py. <br>
Open "GTA San Andreas" video game in fullscreen mode.
## CNN model
Run run_model.py. <br>
Open "GTA San Andreas" video game in fullscreen mode.


# Results
## The autonomous car driving on a highway and dodging other cars
<!-- ![demo 1](https://github.com/yigitatesh/gta_san_andreas_autonomous_driving/blob/main/demos/autonomous_demo_1.gif?raw=true) -->

https://user-images.githubusercontent.com/71609304/137596783-706128fa-574e-4514-8048-977f2ab19fe0.mp4


## The autonomous car dodging another car that is turning into the front of it!
<!-- ![dodging example](https://github.com/yigitatesh/gta_san_andreas_autonomous_driving/blob/main/demos/autonomous_near_miss.gif?raw=true) -->




# Future Improvements
- Collect images with better resolution (needs a large storage space)
- Reduce the number of possible movements (there are 9 movements currently)
- Create a bigger model (bigger kernel sizes, more layers etc.)
- Integrate object detection
