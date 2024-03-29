#!/usr/bin/env python
# coding: utf-8

print("Loading Packages...")
import os
# Do not show unnecessary warning messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import cv2
from mss import mss
import time

from utils.directkeys import PressKey, ReleaseKey, W, A, S, D
from utils.getkeys import get_pressed

import ctypes

import tensorflow as tf
from tensorflow.keras import models

## GET SCREEN WIDTH AND HEIGHT
try:
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
except:
    screensize = input("\nEnter width and height of screen(separated by space): ")
    (width, height) = tuple(map(int, screensize.split()))

# width, height = 800, 600

## SET UP TF ENVIRONMENT
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

## PREPARE MODEL'S INFO
SIZE = 60
EPOCHS = 10

## Model name
# big model v2
MODEL_PREFIX = "gta_sa_{}_epochs_big_v2".format(EPOCHS)
MODEL_NAME = MODEL_PREFIX + ".h5"
MODEL_PATH = "models" + "/" + MODEL_PREFIX + "/" + MODEL_NAME

## LOAD ALEXNET MODEL
print("Loading the Model...")
model = models.load_model(MODEL_PATH)

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
    bbox = {"top": 0, "left": 0, "width": width, "height": height}

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

            ## crop black borders of the game screen
            # thresh black parts
            _,thresh = cv2.threshold(screen, 1, 255, cv2.THRESH_BINARY)
            # find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                cnt = contours[0]
                x, y, w, h = cv2.boundingRect(cnt)
                # crop non-black part of the image
                screen = screen[y:y+h, x:x+w]

            # resize image
            screen = cv2.resize(screen, (SIZE, SIZE))

             # normalize image
            screen = (screen - screen.min()) / max((screen.max() - screen.min()), 0.001)

            ## uncomment below line to see your FPS
            #print("Frame took {} seconds".format(time.time()-last_time))
            last_time = time.time()

            # prediction
            prediction = model.predict(screen.reshape(1, SIZE, SIZE, 1))[0]
            confidence = prediction.max()

            # interpret prediction to move
            #pred_to_move(prediction)
            pred_to_move_with_slow_down(prediction, 0.4)
            
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







