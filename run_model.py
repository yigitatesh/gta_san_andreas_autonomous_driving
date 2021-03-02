#!/usr/bin/env python
# coding: utf-8
import numpy as np
import cv2
from mss import mss
import time
from nn_architectures.alexnet import alexnet

from utils.directkeys import PressKey, ReleaseKey, W, A, S, D
from utils.getkeys import get_pressed

import ctypes

## GET SCREEN WIDTH AND HEIGHT
try:
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
except:
    screensize = input("Enter width and height of screen(separated by space): ")
    (width, height) = tuple(map(int, screensize.split()))

# width, height = 800, 600

## SET UP TF ENVIRONMENT
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

## PREPARE MODEL'S INFO
WIDTH = 80
HEIGHT = 60
LR = 1e-3
EPOCHS = 8

# Model name
# big model v1
MODEL_PREFIX = "gta_sa_lr_{}_{}_{}_epochs_big_v1".format(LR, "alexnet", EPOCHS)

MODEL_NAME = MODEL_PREFIX + ".model"
MODEL_PATH = "models" + "/" + MODEL_PREFIX + "/" + MODEL_NAME

## LOAD ALEXNET MODEL
model = alexnet(WIDTH, HEIGHT, LR)
model.load(MODEL_PATH)

## DIRECTION FUNCTIONS
# movements for 9 choices
def forward():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)

def left():
    PressKey(A)
    ReleaseKey(D)

def right():
    PressKey(D)
    ReleaseKey(A)

def backward():
    PressKey(S)
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)

def no_key():
    ReleaseKey(W)
    ReleaseKey(S)
    ReleaseKey(A)
    ReleaseKey(D)

# Interpreting Predictions to move
# Possible keys or key pairs to one hot array
key_dict = {"A":0, "W":1, "D":2, "S":3, "WA":4, "WD":5, "SA":6, "SD":7, "":8}
key_reverse_list = list(key_dict.keys())

def pred_to_move(prediction):
    """a simple decision function from prediction to movement"""
    # [A, W, D, S, WA, WD, SA, SD, NO_KEY]
    choice = prediction.argmax()
    
    if choice == 0:
        no_key() # reset keys
        left()
        
    elif choice == 1:
        forward()
        
    elif choice == 2:
        no_key() # reset keys
        right()
    elif choice == 3:
        backward()
    elif choice == 4:
        forward()
        left()
    elif choice == 5:
        forward()
        right()
    elif choice == 6:
        backward()
        left()
    elif choice == 7:
        backward()
        right()
    else: # no key
        #no_key()
        forward()

def pred_to_move_with_slow_down(prediction, slow_down_prob=0.1):
    """Decision function which adds some random slowing down probability"""
    # [A, W, D, S, WA, WD, SA, SD, NO_KEY]
    choice = prediction.argmax()
    
    if choice == 0:
        #no_key() # reset keys
        left()
        
    elif choice == 1:
        forward()
        
    elif choice == 2:
        #no_key() # reset keys
        right()
    elif choice == 3:
        backward()
    elif choice == 4:
        forward()
        left()
    elif choice == 5:
        forward()
        right()
    elif choice == 6:
        backward()
        left()
    elif choice == 7:
        backward()
        right()
    else: # no key
        #no_key()
        forward()
    
    random_num = np.random.rand()
    if random_num < slow_down_prob:
        no_key()
        #backward()

## MAIN FUNCTION

def main():
    bbox = {"top": 0, "left": width//10, "width": width*9//10, "height": height}

    sct = mss()
    
    last_time = time.time()
    paused = False
    
    # mainloop
    while True:
        if not paused:
            # get screen
            sct_img = sct.grab(bbox)
            screen = np.array(sct_img)

            # image to grayscale
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

            # resize image
            screen = cv2.resize(screen, (80, 60))

            #cv2.imshow("resized", screen)

            ## uncomment below line to see your FPS
            #print("Frame took {} seconds".format(time.time()-last_time))
            last_time = time.time()

            # prediction
            prediction = model.predict(screen.reshape(1, WIDTH, HEIGHT, 1))[0]
            confidence = prediction.max()

            # interpret prediction to move
            #pred_to_move(prediction)
            pred_to_move_with_slow_down(prediction, 0.2)
            
        # keys
        keys = get_pressed()
        
        # user control
        if "P" in keys:
            # Pause or continue
            if paused:
                paused = False
                time.sleep(1)
            else:
                paused = True
                ReleaseKey(A)
                ReleaseKey(W)
                ReleaseKey(D)
                ReleaseKey(S)
                time.sleep(1)
        elif "B" in keys:
            # Break the loop
            ReleaseKey(A)
            ReleaseKey(W)
            ReleaseKey(D)
            ReleaseKey(S)
            break

if __name__ == "__main__":
    for i in list(range(3))[::-1]:
        print(i+1)
        time.sleep(1)
        
    main()







