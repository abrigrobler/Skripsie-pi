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

# === STREAM ====

class Stream:
	"""
	The stream object is used to check the validity of RTSP sources and create a VideoCapture object using the RTSP source.
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
		'''
		Returns the OpenCV VideoCapture object if a valid source is provided
		'''
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
		ret, frame_orig = self.Stream.get_stream().read()

		if not ret: #Check that a frame is availible
			return False

		frame = frame_orig #Copy the original frame 
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
			cv2.imwrite(img_name, frame_orig) #Save the original frame
			print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

		return True

# === HUMAN DETECTOR ===

class HumanDetector:

	def __init__(self, work_in_dir, interval):
		'''
		work_in_dir : path to the directory in which the class must find images
		interval : interval between directory checks, in minutes
		'''
		self.last_check_time = time.time()
		self.wid = work_in_dir
		self.interval = interval*60
		# initialize the HOG descriptor/person detector
		self.hog = cv2.HOGDescriptor() #which initializes the Histogram of Oriented Gradients descriptor
		self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
		self.imgs_in_dir = 0

		#set the Support Vector Machine to be pre-trained pedestrian detector, loaded via the cv2.HOGDescriptor_getDefaultPeopleDetector() function.

	def detect_and_filter(self):
		'''
		Perform human detection in all saved images using Histograms of Oriented Gradients for Human Detection
		'''

		avg_time = 0

		if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)): #Check that time of interval has passed
			return

		print("[INFO - HumanDetector] Starting detection and filtering of saved images...\n")

		self.last_check_time = time.time() #Update the last checked time
		self.imgs_in_dir = len(os.listdir(self.wid)) #Updates the number of images in the directory in the latest check.
		# These two variables help to optimise the filtering process by only performing the process at specific intervals, and also only when
		# the number of images in the indicated directory has changed

		id_positives = 0
		ac_positives = 0
		imgs_processed = 0

		for img_name in os.listdir(self.wid):

			if img_name and not img_name.startswith('.'): #ignore metadata, corrupt files, etc

				imgs_processed = imgs_processed + 1

				#print("\n[INFO] Img name : {}".format(img_name))	

				cur_time = time.time()

				image = cv2.imread(os. path. join(self.wid,img_name))

				#cv2.imshow("Testing", image)
				image = imutils.resize(image, width=min(400, image.shape[1]))
				orig = image.copy()
				# detect people in the image
				(rects, weights) = self.hog.detectMultiScale(image, winStride=(8, 8),
					padding=(8, 8), scale=1.15)
				# draw the original bounding boxes
				#for (x, y, w, h) in rects:
				#	cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)
				# apply non-maxima suppression to the bounding boxes using a
				# fairly large overlap threshold to try to maintain overlapping
				# boxes that are still people
				#rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
				pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
				# draw the final bounding boxes
				#for (xA, yA, xB, yB) in pick:
				#	cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
				# show some information on the number of bounding boxes
				filename = img_name[img_name.rfind("/") + 1:]
				if len(pick) > 0:
					id_positives = id_positives + 1
					if img_name.startswith('person'):
						ac_positives = ac_positives + 1
					print("[INFO - HumanDetector] {} detections in {}, moving image".format(len(pick),filename))
				else:
					print("[INFO - HumanDetector] Zero detectoins in {}, skipping".format(filename))

				avg_time = avg_time + time.time() - cur_time
			
				# show the output images
				#cv2.imshow("Before NMS", orig)
				#cv2.imshow("After NMS", image)
				#cv2.waitKey(0)

		avg_time = avg_time/imgs_processed

		print("\n[TESTING] Processing of this dataset took {} second, on average, per image".format(avg_time))
		print("[TESTING] A total of {} positives were identified from {} images".format(id_positives, imgs_processed))
		print("[TESTING] {} of the images were correctly identified as positive".format(ac_positives))


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
'''
test = HumanDetector(work_in_dir = '/Volumes/EXPANSION/INRIAPerson/test_imgs', interval = 0.1)

while(True):
	test.detect_and_filter()
'''
		