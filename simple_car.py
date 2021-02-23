#!/usr/bin/env python
# coding: utf-8
import numpy as np
import cv2
from mss import mss
import time

from numpy import ones,vstack
from numpy.linalg import lstsq
from statistics import mean

from utils.directkeys import PressKey, ReleaseKey, W, A, S, D
from utils.getkeys import get_pressed

import ctypes

# get screen width and height
try:
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
except:
    screensize = input("Enter width and height of screen(separated by space): ")
    (width, height) = tuple(map(int, screensize.split()))

width, height = 800, 600

# ## Draw Lines
def draw_lines(image, lines, color=[255, 255, 255], thickness=10):
    """draws lines on an image"""
    try:
        for line in lines:
            coords = np.squeeze(line)
            (x1, y1, x2, y2) = coords
            cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    except:
        pass


# ## Region of Interest
def roi(image, vertices):
    """Gets only region of interest from a binary image"""
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, [vertices], 255)
    masked = cv2.bitwise_and(image, mask)
    
    return masked


# ## Finding 2 Lanes
def get_2_lanes(img, lines, color=[0, 255, 255], thickness=10):
    """gets 2 final average lanes
    Function is inspired from Sentdex
    
    Returns:
    - Lane 1
    - Lane 2
    - slope of Lane 1
    - slope of Lane 2"""
    # if this fails, go with some default line
    try:

        # finds the maximum y value for a lane marker 
        # (since we cannot assume the horizon will always be at the same point.)

        ys = []  
        for i in lines:
            for ii in i:
                ys += [ii[1],ii[3]]
        min_y = min(ys)
        max_y = height
        new_lines = []
        line_dict = {}

        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                m, b = lstsq(A, y_coords)[0]

                # Calculating our new, and improved, xs
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])

        final_lanes = {}

        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]
            
            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy:

                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]

        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]

        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return [int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))]

        lane_1 = average_lane(final_lanes[lane1_id])
        lane_2 = average_lane(final_lanes[lane2_id])

        return lane_1, lane_2, lane1_id, lane2_id
    except:
        pass


# ## Process image
def process_image(original, vertices):
    """Converts original image into a binary image which
    shows the lines in region of interest.
    
    Returns:
    - Processed Image (a binary image)
    - Original Image"""
    # convert to grayscale
    processed = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    
    # median blur to get rid of pepper type noise
    processed = cv2.medianBlur(processed, 3)
    
    # detect edges
    processed = cv2.Canny(processed, threshold1=40, threshold2=200)
    
    # region of interest
    processed = roi(processed, vertices)
    #return processed, original
    
    # apply Gaussian Blur
    processed = cv2.GaussianBlur(processed, (5, 5), 0)
    
    return processed, original


# ## Direction Functions
def straight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    
def left():
    PressKey(W)
    PressKey(A)
    ReleaseKey(D)
    
def right():
    PressKey(W)
    PressKey(D)
    ReleaseKey(A)
    
def slow_down():
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(D)


# ## Decision Functions
def simple_decision(m1, m2):
    """Simple decision by looking slopes of 2 lanes"""
    if m1 < 0 and m2 < 0:
        right()
    elif m1 > 0 and m2 > 0:
        left()
    else:
        straight()

def simple_decision_with_slow_down(m1, m2, slow_prob=0.2):
    """Sometimes slows down instead of fully going forward"""
    if m1 < 0 and m2 < 0:
        right()
    elif m1 > 0 and m2 > 0:
        left()
    else:
        random_num = np.random.rand()
        if random_num > slow_prob:
            straight()
        else:
            slow_down()

def simple_decision_with_slow_down_and_slow_turn(m1, m2, slow_prob=0.2,
                                                leave_turn_prob=0.3):
    """Releasing turn keys after tapping to turn keys according to a probability"""
    if m1 < 0 and m2 < 0:
        right()
        random_num = np.random.rand()
        if random_num < leave_turn_prob:
            ReleaseKey(D)
            
    elif m1 > 0 and m2 > 0:
        left()
        random_num = np.random.rand()
        if random_num < leave_turn_prob:
            ReleaseKey(A)
            
    else:
        random_num = np.random.rand()
        if random_num > slow_prob:
            straight()
        else:
            slow_down()


# ## Main Function
def main():
    bbox = {"top": 0, "left": 0, "width": width, "height": height}

    sct = mss()
    
    # vertices for region of interest
    # from left bottom and clockwise
    vertices = np.array([[0, height-1], [0, height*5//8], 
                         [width*2//5, height//2], [width*3//5, height//2],
                         [width-1, height*5//8], [width-1, height-1]])

    paused = False
    
    # mainloop
    while True:
        if not paused:
            # get screen
            sct_img = sct.grab(bbox)
            screen = np.array(sct_img)

            # process screen
            processed, original = process_image(screen, vertices)
            
            # find lines
            lines = cv2.HoughLinesP(processed, 1, np.pi/180, 150, np.array([]), 20, 15)
            
            # find lanes
            m1, m2, l1, l2 = 0, 0, 0, 0 # default values
            ret = get_2_lanes(original, lines)
            if ret:
                (l1, l2, m1, m2) = ret
            lanes = [l1, l2]
            
            # simple decision
            #simple_decision(m1, m2)
            #simple_decision_with_slow_down(m1, m2, 0.3)
            simple_decision_with_slow_down_and_slow_turn(m1, m2, 0.4, 0.2)
            
            # draw lines and lanes
            #draw_lines(processed, lines)
            #draw_lines(original, lanes, color=[0, 255, 0], thickness=20)

            #cv2.imshow("processed", processed)
            #cv2.imshow("original", original)

            #if cv2.waitKey(1) & 0xFF == ord("q"):
                #cv2.destroyAllWindows()
                #break

        # keys and user control
        keys = get_pressed()

        if "P" in keys:
            # pause or continue
            if paused:
                paused = False
                time.sleep(1)
            else:
                paused = True
                ReleaseKey(A)
                ReleaseKey(W)
                ReleaseKey(D)
                time.sleep(1)
        elif "B" in keys:
            # close the app
            ReleaseKey(A)
            ReleaseKey(W)
            ReleaseKey(D)
            break


if __name__ == "__main__":
    print("Starting...")
    for i in list(range(3))[::-1]:
        print(i+1)
        time.sleep(1)
    print("Started.")
        
    main()
