# Grand Theft Auto San Andreas Autonomous Driving
Autonomous driving in the game "Grand Theft Auto San Andreas"

# Summary
Includes some different techniques and models for autonomous driving from simple road lane detector model to CNN models. <br>
There are two models now:

## Simple Car model
It is based on road lanes and makes decisions by looking at road lanes. <br>
Not AI based.

## CNN model
It is based on CNN and trained by 45.000 images. <br>
The program takes a screenshot of the game window and predicts the best move for that time with CNN model.

# Requirements
## For Simple Car model (simple_car.py)
- opencv
- mss
- win32api
## For CNN Model (run_model.py)
- tensorflow-gpu
- cuda and cudnn support
- tflearn
- opencv
- mss
- win32api

# How to Run
## Simple car model
Run simple_car.py
## CNN model
Run run_model.py

# Results
## Demo showing the autonomous car dodging another car
![dodging example](https://github.com/yigitatesh/gta_san_andreas_autonomous_driving/blob/main/demos/autonomous_near_miss.gif?raw=true)
