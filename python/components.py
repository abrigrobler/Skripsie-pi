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
from threading import Lock
import glob

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
	"""
	cap = cv2.VideoCapture()

	# From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv

	last_frame = None
	last_ready = None
	lock = Lock()

	def __init__(self, src='', test_source = False):
		global cap
		self.src = src


		if not test_source:
			if src == '0' or src == ':@0:': #Enable webcam support
				self.cap = cv2.VideoCapture(0)
			else:
				rtsp_string = 'rtsp://' + src
				self.cap = cv2.VideoCapture(rtsp_string)
		else:
			self.cap = cv2.VideoCapture(src)

		# From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv
		thread = threading.Thread(target=self.rtsp_cam_buffer, args=(self.cap,), name="rtsp_read_thread")
		thread.daemon = True
		thread.start()

	# From https://stackoverflow.com/questions/51722319/skip-frames-and-seek-to-end-of-rtsp-stream-in-opencv

	def rtsp_cam_buffer(self, capture):
		while True:
			with self.lock:
				self.last_ready, self.last_frame = capture.read()

	def get_stream(self):
		'''
		Returns the OpenCV VideoCapture object if a valid source is provided, and if a frame is available
		'''
		if (self.last_ready is not None) and (self.last_frame is not None):
			if self.src == '':
				print("[ERROR - Stream] No source provided to stream from")
				return None
			else:
				return self.last_frame.copy()
		else:
			return None

# === MOTION DETECTOR ===

class MotionDetector:

	"""
	This class will hold a single stream, and perform background subtraction on the stream. Images on which motion are detected will be saved.
	"""

	def __init__(self, stream, name, filepath, min_area, width = 800):
		self.Stream = stream
		self.width = width
		self.name = name
		self.filepath = filepath
		self.min_area = min_area
		self.fg_detect = cv2.createBackgroundSubtractorKNN()
		self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))

	def process_single_frame(self):
		"""
		This method will be called in a while loop in another script. Therefore, it will only apply to a single frame.
		"""
		frame_orig = self.Stream.get_stream()

		#print("[DEBUG] ",frame_orig)

		if frame_orig is None: #Check that a frame is available
			return None

		frame = frame_orig #Copy the original frame 
		frame = imutils.resize(frame, self.width)
		fg_mask = self.fg_detect.apply(frame)

		fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel) #Remove noise

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
			#cv2.imshow("Frame Delta", fg_mask)
			#cv2.imshow("Security Feed", frame)
			#print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

		#return True

# === MOTION DETECTOR WITH LOWER FRAME RATE ===

class MotionDetectorLFR:

	"""
	This class will hold a single stream, and perform background subtraction on the stream. Images on which motion are detected will be saved.
	In addition, the frame rate is forced to 1 frame per second. This is done in order to lighten the processing load,
	and also under the assumption that no details will be misssed with a low framerate. A lower framerate also helps
	to reduce the number of images saved by the algorithm.
	"""
	frame = 0

	def __init__(self, stream, name, filepath, min_area, width = 800, initial_frame_skip = 20):
		self.Stream = stream
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

		#print("[DEBUG] ",frame_orig)

		if frame_orig is None: #Check that a frame is available
			return None
			
		if self.frame < self.initial_frame_skip: #Skip frames during which the background subtractor initializes
			self.frame = self.frame + 1
			return None

		frame = frame_orig #Copy the original frame 
		frame = imutils.resize(frame, self.width)
		fg_mask = self.fg_detect.apply(frame)

		fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel) #Remove noise

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
			#cv2.imshow("Frame Delta", fg_mask)
			#cv2.imshow("Security Feed", frame)
			#print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

		#return True

# === MOTION DETECTOR 2 ===

class MotionDetector2:

	"""
	This class will hold a single stream, and perform background subtraction on the stream. Images on which motion are detected will be saved.

	The idea of this experimental class is to generate an activity heatmap from 10 frames every [interval] minutes, and then compare the position
	of detected motion to the heatmap, to only save images where motion was detected in 'cold' zones.
	"""
	hm_list = []
	last_check_time = 0
	heatmap_generated = False
	current_frame = 0
	initial_frames = 0

	def __init__(self, stream, name, filepath, min_area, width = 800, interval = 2, hm_frame_count = 5000, hm_min_area = 10, hm_threshold = 10):
		self.Stream = stream
		self.width = width
		self.name = name
		self.interval = interval * 60
		self.filepath = filepath
		self.min_area = min_area
		self.hm_frame_count = hm_frame_count
		self.hm_min_area = hm_min_area
		self.hm_threshold = hm_threshold
		self.fg_detect = cv2.createBackgroundSubtractorKNN()
		self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))

	def generate_heatmap(self, frame):

		'''
		Generates and saves a heatmap
		'''
		self.last_check_time = time.time()


		self.current_frame = self.current_frame + 1
		if self.current_frame > 20:
			self.hm_list.append(frame)
		#cv2.imshow("Current frame", frame)

		#cv2.waitKey(0)

		if self.current_frame >= self.hm_frame_count:
			heatmap = sum(self.hm_list)
			blur = cv2.GaussianBlur(heatmap,(27,27),0)
			#blur = cv2.applyColorMap(blur, cv2.COLORMAP_JET)
			self.heatmap_generated = True

			cv2.imwrite('../bin/heatmaps/' + self.name + '.jpg', blur)

			print("[INFO] Heatmap generated.")


	def process_single_frame(self):
		"""
		This method will be called in a while loop in another script. Therefore, it will only apply to a single frame.
		"""
		frame_orig = self.Stream.get_stream()

		#print("[DEBUG] ",frame_orig)

		if frame_orig is None: #Check that a frame is available
			return None

		self.initial_frames = self.initial_frames + 1

		if self.initial_frames < 100:
			return None

		frame = frame_orig #Copy the original frame 
		frame = imutils.resize(frame, self.width)
		fg_mask = self.fg_detect.apply(frame)

		fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel) #Remove noise

		cnts = cv2.findContours(fg_mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)

		if not time.time() - self.last_check_time < self.interval and self.last_check_time > 0:
			print("[INFO] A heatmap is being generated")
			self.heatmap_generated = False
			self.current_frame = 0

		
		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it

			if not self.heatmap_generated:
				if cv2.contourArea(c) < self.hm_min_area:
					continue
				self.generate_heatmap(fg_mask)
			else:
				if cv2.contourArea(c) < self.min_area:
					continue



				hm_name = '../bin/heatmaps/' + self.name + '.jpg'
				compare_to_hm = cv2.imread(hm_name)

				# From https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
				'''
				The idea here is to compare the centroid of the detected contour to the heatmap, and determine whether or not
				this is in a cold zone
				'''
				(y,x), _ = cv2.minEnclosingCircle(c)

				x = int(x)
				y = int(y)

				#print("X: {}, Y: {}".format(x, y))

				color = compare_to_hm[x, y]
				#print(color)

				if color[0] > self.hm_threshold:
					#print("[INFO] Motion detected in cold zone")
					img_name = self.filepath + self.name + " - " + datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p") + '.jpg'
					cv2.imwrite(img_name, frame_orig) #Save the original frame
				#cv2.imshow("Frame Delta", fg_mask)
				#cv2.imshow("Security Feed", frame)
				#print("[INFO - MotionDetector] Motion detected on " + self.name + ", frame saved")

		#return True

# === HUMAN DETECTOR ===

class HumanDetector:

	first_pass_completed = False

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

		if self.first_pass_completed:
			if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)): #Check that time of interval has passed
				return

		self.first_pass_completed = True

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
				image = imutils.resize(image, width=min(700, image.shape[1]))
				orig = image.copy()
				# detect people in the image
				(rects, weights) = self.hog.detectMultiScale(image, winStride=(4, 4),
					padding=(8, 8), scale=1.13)
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
					os.rename("../bin/saved_images/" + img_name, "../bin/human_images/" + img_name) #Move the image
					#cv2.imshow('Detection', image)
					#cv2.waitKey(0)
					if img_name.startswith('person'):
						ac_positives = ac_positives + 1
					print("[INFO - HumanDetector] {} detections in {}, moving image".format(len(pick),filename))
				else:
					#print("[INFO - HumanDetector] Zero detections in {}, skipping".format(filename))
					pass

				avg_time = avg_time + time.time() - cur_time
			
				# show the output images
				#cv2.imshow("Before NMS", orig)
				#cv2.imshow("After NMS", image)
				#cv2.waitKey(0)

		avg_time = avg_time/imgs_processed

		print("\n[TESTING] Processing of this dataset took {} second, on average, per image".format(avg_time))
		print("[TESTING] A total of {} negatives were identified from {} images".format(id_positives, imgs_processed))

# === SIMILARITY DETECTOR ===

class SimilarityDetector:

	first_image = None
	first_pass_completed = False

	def __init__(self, work_in_dir, interval, similarity_thresh = 92):
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

		#first_image_hist = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
		#second_image_hist = cv2.calcHist([current_frame], [0], None, [256], [0, 256])

		#img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_CORREL)
		img_template_probability_match = cv2.matchTemplate(prev_frame, current_frame, cv2.TM_CCOEFF_NORMED)[0][0]

		# taking only 10% of histogram diff, since it's less accurate than template method
		commutative_image_match = (img_template_probability_match)*100
		print("[DEBUG - SimilarityDetector] Image similarity: ", commutative_image_match)
		return commutative_image_match

	def match_and_filter(self):
		'''
		Perform human detection in all saved images using Histograms of Oriented Gradients for Human Detection
		'''

		#avg_time = 0
		if self.first_pass_completed:
			if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)) or len(os.listdir(self.wid)) < 2: #Check that time of interval has passed
				return

		print("[INFO - SimilarityDetector2] Starting matching and filtering of saved images...\n")

		self.last_check_time = time.time() #Update the last checked time
		self.imgs_in_dir = len(os.listdir(self.wid)) #Updates the number of images in the directory in the latest check.
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
				print("[DEBUG - SimilarityDetector2] Image below threshold found")
				os.rename(img_name, "../bin/storage/" + img_name[19:]) #Move the image

			self.first_image = image


# === SIMILARITY DETECTOR 2 ===

class SimilarityDetector2:

	first_image = None
	first_pass_completed = False

	def __init__(self, work_in_dir, interval, similarity_thresh = 93):
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

		first_image_hist = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
		second_image_hist = cv2.calcHist([current_frame], [0], None, [256], [0, 256])

		img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_CORREL)
		img_template_probability_match = cv2.matchTemplate(prev_frame, current_frame, cv2.TM_CCOEFF_NORMED)[0][0]

		commutative_image_match = (0.5*img_template_probability_match + 0.5*img_hist_diff)*100
		print("[DEBUG - SimilarityDetector] Image similarity: ", commutative_image_match)
		return commutative_image_match

	def match_and_filter(self):

		#avg_time = 0
		if self.first_pass_completed:
			if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)) or len(os.listdir(self.wid)) < 2: #Check that time of interval has passed
				return

		print("[INFO - SimilarityDetector2] Starting matching and filtering of saved images...\n")

		self.last_check_time = time.time() #Update the last checked time
		self.imgs_in_dir = len(os.listdir(self.wid)) #Updates the number of images in the directory in the latest check.
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
				print("[DEBUG - SimilarityDetector2] Image below threshold found")
				os.rename(img_name, "../bin/storage/" + img_name[19:]) #Move the image

			self.first_image = image

				#avg_time = avg_time + time.time() - cur_time

		#avg_time = avg_time/imgs_processed

		'''
		print("[TESTING] Processing of this dataset took {} second, on average, per image".format(avg_time))
		print("[TESTING] A total of {} positives were identified from {} images".format(id_positives, imgs_processed))
		print("[TESTING] {} of the images were correctly identified as positive".format(ac_positives))
		'''

# === SIMILARITY DETECTOR 3 ===

class SimilarityDetector3:
	'''
	The third version of the SD actually compares each image to all other images in the directory
	The problem here is that it takes way too long, and simply yields bad results.
	'''


	first_image = None
	first_pass_completed = False

	def __init__(self, work_in_dir, interval, similarity_thresh = 93):
		'''
		work_in_dir : path to the directory in which the class must find images
		interval : interval between directory checks, in minutes
		'''
		self.last_check_time = time.time()
		self.wid = work_in_dir
		self.interval = interval*60
		self.imgs_in_dir = 0
		self.similarity_thresh = similarity_thresh

		self.files = glob.glob(self.wid + '/*.jpg')
		self.files.sort(key=os.path.getmtime)

	def determine_similarity(self, prev_frame, current_frame):
		# FROM https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv

		first_image_hist = cv2.calcHist([prev_frame], [0], None, [256], [0, 256])
		second_image_hist = cv2.calcHist([current_frame], [0], None, [256], [0, 256])

		img_hist_diff = cv2.compareHist(first_image_hist, second_image_hist, cv2.HISTCMP_CORREL)
		#img_template_probability_match = cv2.matchTemplate(prev_frame, current_frame, cv2.TM_CCOEFF_NORMED)[0][0]

		# taking only 10% of histogram diff, since it's less accurate than template method
		commutative_image_match = (img_hist_diff)*100
		#print("[DEBUG - SimilarityDetector] Image similarity: ", commutative_image_match)
		return commutative_image_match

	def match_and_filter(self):
		start_time = time.time()
		'''
		Perform human detection in all saved images using Histograms of Oriented Gradients for Human Detection
		'''

		#avg_time = 0
		if self.first_pass_completed:
			if (time.time() - self.last_check_time < self.interval) or self.imgs_in_dir == len(os.listdir(self.wid)) or len(os.listdir(self.wid)) < 2: #Check that time of interval has passed
				return

		#print("[INFO - SimilarityDetector2] Starting matching and filtering of saved images...\n")

		self.first_pass_completed = True

		self.last_check_time = time.time() #Update the last checked time
		self.imgs_in_dir = len(os.listdir(self.wid)) #Updates the number of images in the directory in the latest check.
		# These two variables help to optimise the filtering process by only performing the process at specific intervals, and also only when
		# the number of images in the indicated directory has changed
		

		iter = 0
		for img_name in self.files:
			print("CHECKING IMAGE", img_name)
			iter = iter + 1
			
			for comp_image_name in self.files:

				if comp_image_name == img_name:
					continue
			
				image_current = cv2.imread(img_name)
				image_compare = cv2.imread(comp_image_name)

				SIM = self.determine_similarity(image_current, image_compare)

				if SIM > self.similarity_thresh:
					'''
					Save the image if the similarity is less than the set threshold
					''' 
					print("[DEBUG - SimilarityDetector3] Similar image found")
					os.rename(comp_image_name, "../bin/storage/" + comp_image_name[19:]) #Move the image
					self.files.remove(comp_image_name)

		print("[INFO - SimilarityDetector3] Match and filter completed. Time:", time.time() - start_time)

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

		