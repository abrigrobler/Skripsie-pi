'''
-----------------------------------------------
title: components.py
description: Classes created for use in the GUI.py app, in order to hold all reusable methods and classes which clutter up the other scripts
author: AF Grobler
for: Project (E) 448, Department of Electric and Electronic Engineering, University of Stellenbosch
-----------------------------------------------
'''

import cv2
import PIL
from PIL import Image, ImageTk
import pickle
import sys
import os
import time
import datetime
import numpy as np
import imutils

# === STREAM ====

class Stream:
    """
    The stream object is used to check the validity of RTSP sources, and also to actually create and view a stream in GUI.py
    cap - cv2 video capture object
    src - defines the source (rtsp string) of the video capture object
    """
    cap = cv2.VideoCapture()

    def __init__(self, src='', test_source = False):
        global cap
        self.src = src

        if not test_source:
            if src == '0' or src == ':@0:': #Enable webcam support
                self.cap = cv2.VideoCapture(0)
            else:
                rtsp_string = 'rtsp://' + src + '/videoMain'
                self.cap = cv2.VideoCapture(rtsp_string)
        else:
            self.cap = cv2.VideoCapture(src)

    def get_stream(self):
        if self.src == '':
            return False
        else:
            return self.cap

# === MOTION DETECTOR ===

class MotionDetector:

    """
    This class will hold a single stream, and perform background subtraction on the stream. Images on which motion are detected will be saved.
    """

    def __init__(self, stream, name, filepath, min_area, width = 500):
        self.Stream = stream
        self.width = width
        self.name = name
        self.filepath = filepath
        self.min_area = min_area
        self.fg_detect = cv2.createBackgroundSubtractorKNN()

    def process_single_frame(self):
        """
        This method will be called in a while loop in another script. Therefore, it will only apply to a single frame.
        """
        ret, frame = self.Stream.get_stream().read()

        if not ret: #Check that a frame is availible
            return False


        frame = imutils.resize(frame, self.width)
        fg_mask = self.fg_detect.apply(frame)

        cnts = cv2.findContours(fg_mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.min_area:
                continue

            img_name = self.filepath + self.name + " - " + datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p") + '.jpg'
            cv2.imwrite(img_name, frame) #Saving
            print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

        return True

class CameraManager:

    def list_cameras(filepath):
        """
        Reads the saved camera information from a .pickle file, and returns a list containing the information.
        """

        cam_list = []

        if not os.path.isfile(filepath + 'saved_cameras.pickle'):
            print("[INFO - CameraManager] No saved cameras exist on this device yet")
            return False

        f = open(filepath + 'saved_cameras.pickle', 'rb')
        print("[INFO - CameraManager] Fetching saved cameras")
        cam_dict = pickle.load(f)

        for cam in cam_dict:
            cam_list.append([cam, cam_dict[cam]])

        f.close()

        return cam_list

    def save_camera(filepath, window, name, src):
        """
        Writes the info of a new camera to the file. Also performs a check for file existence, and rejects duplicates
        """

        if not os.path.isfile(filepath + 'saved_cameras.pickle'):
            print("[INFO - CameraManager] Creating save file")
            f = open(filepath + 'saved_cameras.pickle', 'wb')
            pickle.dump({}, f)
            f.close()

        f = open(filepath + 'saved_cameras.pickle', 'rb')

        cam_dict = pickle.load(f)
        for cam in cam_dict:
            if cam_dict[cam] == src:
                print("[ERROR - CameraManager] A camera with this source has already been added. Rejecting duplicate")
                f.close()
                window.destroy()
                return

        f.close()


        f = open(filepath + 'saved_cameras.pickle', 'wb')
        print("[INFO - CameraManager] Saving current camera")
        cam_dict.update( {name : src})

        pickle.dump(cam_dict, f)
        f.close()

        print("[INFO - CameraManager] Camera saved")

        window.destroy()

        return

    def delete_camera(window, filepath, name):

        """
        Deletes a named camera from the saved file
        """

        if not os.path.isfile(filepath + 'saved_cameras.pickle'):
            print("[INFO - CameraManager] No saved cameras exist on this device yet")
            return

        f = open(filepath + 'saved_cameras.pickle', 'rb')
        print("[INFO - CameraManager] Fetching saved cameras")
        cam_dict = pickle.load(f)
        f.close()

        del cam_dict[name]
        print("[INFO - CameraManager] " + name + " has been removed")
        f = open(filepath + 'saved_cameras.pickle', 'wb')
        pickle.dump(cam_dict, f)
        f.close()

        window.destroy()

        return





        