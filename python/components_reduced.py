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
from imutils.object_detection import non_max_suppression
import threading
from threading import Lock, Thread
import glob
import shutil
import random

# === STREAM ====

class Stream:
    """
    The stream object is used to check the validity of RTSP sources and create a VideoCapture object using the RTSP source.
    cap - cv2 video capture object
    src - defines the source (rtsp string) of the video capture object

    The issue here is that once the processor and stream goes out of sync, the feed completely stops. Which
    means some sort of buffer is required, either to skip frames to keep the sync, or to hold frames for when
    the processor is ready for the next frame. The overflow, if any, can then be discarded.

    This is only required for continuous streams, and not for videos or image sequences.

    A threading fix has been implemented to try and fix this.
    Seems to be working now, for the most part at least.

    In addition, the stream needs to be refreshed at some points in time to resync the source and processor
    """
    cap: cv2.VideoCapture()

    # From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv

    last_frame = None
    last_ready = None
    lock = Lock()

    def __init__(self, src='', test_source=False):
        global cap
        self.src = src

        if not test_source:
            if src == '0' or src == ':@0:':  # Enable webcam support
                self.cap = cv2.VideoCapture(0)
            else:
                rtsp_string = 'rtsp://' + src
                self.cap = cv2.VideoCapture(rtsp_string)
        else:
            self.cap = cv2.VideoCapture(src)

        # From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv
        thread = threading.Thread(target=self.rtsp_cam_buffer, args=(
            self.cap,), name="rtsp_read_thread")
        thread.daemon = True
        thread.start()

    # From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv

    def rtsp_cam_buffer(self, capture):
        while True:
            with self.lock:
                self.last_ready, self.last_frame = capture.read()

    def get_stream(self):
        '''
        Returns a frame if a valid source is provided, and if a frame is available
        '''
        if (self.last_ready is not None) and (self.last_frame is not None):
            if self.src == '':
                print("[ERROR - Stream] No source provided to stream from")
                return None
            else:
                return self.last_frame.copy()
        else:
            return None

    def refresh_stream(self):
        self.cap = None
        time.sleep(2)
        if self.src == '0' or self.src == ':@0:':  # Enable webcam support
            self.cap = cv2.VideoCapture(0)
        else:
            rtsp_string = 'rtsp://' + self.src
            self.cap = cv2.VideoCapture(rtsp_string)

    def release_stream(self):
        self.cap.release()
        self.cap = None
        
# === MOTION DETECTOR WITH FORCED LOWERED FRAME RATE ===

class MotionDetectorLFR:

    """
    This class will hold a single stream, and perform background subtraction on the stream. Images on which motion are detected will be saved.
    In addition, the frame rate is forced to 1 frame per second. This is done in order to lighten the processing load,
    and also under the assumption that no details will be misssed with a low framerate. A lower framerate also helps
    to reduce the number of images saved by the algorithm.
    """
    frame = 0

    def __init__(self, stream, name, filepath, min_area, width=800, initial_frame_skip=20):
        self.refresh_rate = 4*60
        self.last_check_time = time.time()
        self.Stream = stream
        self.stream_data = stream
        self.width = width
        self.name = name
        self.filepath = filepath
        self.min_area = min_area
        self.start_time = time.time()
        self.fg_detect = cv2.createBackgroundSubtractorKNN()
        self.initial_frame_skip = initial_frame_skip
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))

    def process_single_frame(self):
        """
        This method will be called in a while loop in another script. Therefore, it will only apply to a single frame.
        """

        if time.time() - self.start_time < 1:
            return None

        self.start_time = time.time()
        frame_orig = self.Stream.get_stream()

        # print("[DEBUG] ",frame_orig)

        if frame_orig is None:  # Check that a frame is available
            return None

        if self.frame < self.initial_frame_skip:  # Skip frames during which the background subtractor initializes
            self.frame = self.frame + 1
            return None

        frame = frame_orig  # Copy the original frame
        frame = imutils.resize(frame, self.width)
        fg_mask = self.fg_detect.apply(frame)

        fg_mask = cv2.morphologyEx(
            fg_mask, cv2.MORPH_OPEN, self.kernel)  # Remove noise

        cnts = cv2.findContours(fg_mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.min_area:
                continue

            img_name = self.filepath + self.name + " - " + \
                datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p") + '.jpg'
            cv2.imwrite(img_name, frame_orig)  # Save the original frame
            # cv2.imshow("Frame Delta", fg_mask)
            # cv2.imshow("Security Feed", frame)
            # print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

        if time.time() - self.last_check_time > self.refresh_rate:
            # Refresh the incoming stream to avoid getting too far out of sync
            print("[INFO - MotionDetector]Refreshing stream data on " + self.name)
            self.Stream.refresh_stream()
            self.last_check_time = time.time()

        # return True

# === HUMAN DETECTOR UTILITY===

class HumanDetectorUtil:
    '''
    Instead of using HOG, this second implementation of a human detector will use a HAAR cascade classifier
    '''

    def __init__(self):
        '''
        work_in_dir : path to the directory in which the class must find images
        interval : interval between directory checks, in minutes
        '''
        # initialize the cascade classifier
        self.classifier = cv2.CascadeClassifier()
        if not self.classifier.load(cv2.samples.findFile('../bin/cascades/haarcascade_fullbody.xml')):
            print("[ERROR - HumanDetector2] Failed to find feature file.")
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame):

        image = imutils.resize(frame, width=min(700, frame.shape[1]))

        # detect people in the image
        # The greyscale image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bodies = self.classifier.detectMultiScale(gray)

        (rects, weights) = self.hog.detectMultiScale(image, winStride=(4, 4),
                                                     padding=(8, 8), scale=1.13)

        pick = non_max_suppression(
            rects, probs=None, overlapThresh=0.65)

        if len(bodies) > 0 or len(pick) > 0:
            return True

        else:
            return False

# === SIMILARITY DETECTOR ===

class SimilarityDetector:

    first_image = None
    first_pass_completed = True

    def __init__(self, work_in_dir, interval, similarity_thresh=93):
        '''
        work_in_dir : path to the directory in which the class must find images
        interval : interval between directory checks, in minutes
        '''
        self.last_check_time = time.time()
        self.wid = work_in_dir
        self.interval = interval*60
        self.imgs_in_dir = 0
        self.similarity_thresh = similarity_thresh

    def determine_similarity(self, prev_frame, current_frame):
        # FROM https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv
        prev_frame = imutils.resize(prev_frame, 700)
        current_frame = imutils.resize(current_frame, 700)

        first_image_hist = cv2.calcHist(
            [prev_frame], [0], None, [256], [0, 256])
        second_image_hist = cv2.calcHist(
            [current_frame], [0], None, [256], [0, 256])

        img_hist_diff = cv2.compareHist(
            first_image_hist, second_image_hist, cv2.HISTCMP_CORREL)
        img_template_probability_match = cv2.matchTemplate(
            prev_frame, current_frame, cv2.TM_CCOEFF_NORMED)[0][0]

        commutative_image_match = (
            0.5*img_template_probability_match + 0.5*img_hist_diff)*100
        print("[DEBUG - SimilarityDetector] Image similarity: ",
              commutative_image_match)
        return commutative_image_match

    def match_and_filter(self):

        # avg_time = 0
        if self.first_pass_completed:
            # Check that time of interval has passed
            if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)) or len(os.listdir(self.wid)) < 2:
                return

        print(
            "[INFO - SimilarityDetector] Starting matching and filtering of saved images...\n")

        self.last_check_time = time.time()  # Update the last checked time
        # Updates the number of images in the directory in the latest check.
        self.imgs_in_dir = len(os.listdir(self.wid))
        # These two variables help to optimise the filtering process by only performing the process at specific intervals, and also only when
        # the number of images in the indicated directory has changed
        files = glob.glob(self.wid + '/*.jpg')
        files.sort(key=os.path.getmtime)

        for img_name in files:

            if self.first_image is None:
                self.first_image = cv2.imread(img_name)
                self.first_pass_completed = True
                continue

            image = cv2.imread(img_name)

            SIM = self.determine_similarity(self.first_image, image)

            if SIM > self.similarity_thresh:
                '''
                Save the image if the similarity is less than the set threshold
                '''
                print("[DEBUG - SimilarityDetector] Image below threshold found")
                os.rename(img_name, "../bin/storage/" +
                          img_name[19:])  # Move the image

            self.first_image = image

# === STORAGE MANAGER ===

class StorageManager:
    '''
    This class will periodically check the available free space in the working directory, and select images at random to delete.
    If the image contains features
    '''
    force_remove = False
    memory_flag: bool
    first_pass_completed = True

    def __init__(self, work_in_dir, interval, space=20, critical_space=2):
        '''
        work_in_dir : path to the directory in which the class must find images
        interval : interval between directory checks, in minutes
        '''
        self.last_check_time = time.time()
        self.wid = work_in_dir
        self.interval = interval*60
        self.files = glob.glob(self.wid + '/*.jpg')
        self.files.sort(key=os.path.getmtime)
        self.required_space = space
        self.critical_space = critical_space
        self.detector_util = HumanDetectorUtil()

    def check_free_space(self):
        total, used, free = shutil.disk_usage("/")
        #print ("Total free space on system: %d GiB" % (free // (2**30)))
        return (free // (2**30))

    def reduce_files(self):
        '''
        Perform human detection in all saved images using Histograms of Oriented Gradients for Human Detection
        '''
        space = self.check_free_space()
        if space < self.required_space:
            self.memory_flag = True
        else:
            self.memory_flag = False

        if space < self.critical_space:
            self.force_remove = True
        else:
            self.force_remove = False

        if self.first_pass_completed:
            # Check that time of interval has passed
            if (time.time() - self.last_check_time < self.interval) and not self.memory_flag:
                return

        print("[INFO] Cleaning memory")

        self.files = glob.glob(self.wid + '/*.jpg')

        if len(self.files) > 10:
            rand_img = random.choice(self.files)
            img = cv2.imread(rand_img)

            if self.detector_util.detect(img) and not self.force_remove:
                return None
            else:
                os.remove(rand_img)
                self.files.remove(rand_img)

        self.last_check_time = time.time()

# === CAMERA MANAGER ===

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
                print(
                    "[ERROR - CameraManager] A camera with this source has already been added. Rejecting duplicate")
                f.close()
                window.destroy()
                return

        f.close()

        f = open(filepath + 'saved_cameras.pickle', 'wb')
        print("[INFO - CameraManager] Saving current camera")
        cam_dict.update({name: src})

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
    
# === SYSTEM CLASSES TO HANDLE MULTIPLE STREAMS AND SOURCES ===

class SystemMotionDetection:

    def start(min_area = 1250):
        MD_list = []
        cam_list = CameraManager.list_cameras('../bin/')

        for c in cam_list:
            MD_list.append(MotionDetectorLFR(stream=Stream(
                c[1]), name=c[0], min_area=min_area, filepath=str('../bin/' + c[0] + '/')))

        while(True):
            for MD in MD_list:
                MD.process_single_frame()


class SystemFiltering:

    def start(filter_interval=10):

        SD_list = []
        cam_list = CameraManager.list_cameras('../bin/')

        for c in cam_list:
            SD_list.append(SimilarityDetector(work_in_dir=str(
                '../bin/' + c[0] + '/'), interval=filter_interval, similarity_thresh=93))

        while(True):
            for SD in SD_list:
                SD.match_and_filter()