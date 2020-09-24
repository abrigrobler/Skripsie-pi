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

class Stream:
	'''
	The stream object is used to check the validity of RTSP sources, and also to actually create and view a stream in GUI.py
	'''
	cap = cv2.VideoCapture()

	def __init__(self, src=''):
		global cap
		self.src = src
		self.streaming = False

		if src == '0' or src == ':@0:': #Enable webcam support
			self.cap = cv2.VideoCapture(0)
		else:
			rtsp_string = 'rtsp://' + src + '/videoMain'
			self.cap = cv2.VideoCapture(rtsp_string)

	def get_stream(self):
		if self.src == '':
			return False
		else:
			return self.cap

class CameraManager:

	def list_cameras(filepath):
		'''
		Reads the saved camera information from a .pickle file, and returns a list containing the information.
		'''

		cam_list = []

		if not os.path.isfile(filepath + 'saved_cameras.pickle'):
			print("[INFO] No saved cameras exist on this device yet")
			return False

		f = open(filepath + 'saved_cameras.pickle', 'rb')
		print("[INFO] Fetching saved cameras")
		cam_dict = pickle.load(f)

		for cam in cam_dict:
			cam_list.append([cam, cam_dict[cam]])

		f.close()

		return cam_list

	def save_camera(filepath, window, name, src):
		'''
		Writes the info of a new camera to the file. Also performs a check for file existence, and rejects duplicates
		'''

		if not os.path.isfile(filepath + 'saved_cameras.pickle'):
			print("[INFO] Creating save file")
			f = open(filepath + 'saved_cameras.pickle', 'wb')
			pickle.dump({}, f)
			f.close()

		f = open(filepath + 'saved_cameras.pickle', 'rb')

		cam_dict = pickle.load(f)
		for cam in cam_dict:
			if cam_dict[cam] == src:
				print("[ERROR] A camera with this source has already been added. Rejecting duplicate")
				f.close()
				window.destroy()
				return

		f.close()


		f = open(filepath + 'saved_cameras.pickle', 'wb')
		print("[INFO] Saving current camera")
		cam_dict.update( {name : src})

		pickle.dump(cam_dict, f)
		f.close()

		print("[INFO] Camera saved")

		window.destroy()

		return

	def delete_camera(window, filepath, name):

		'''
		Deletes a named camera from the saved file
		'''

		if not os.path.isfile(filepath + 'saved_cameras.pickle'):
			print("[INFO] No saved cameras exist on this device yet")
			return

		f = open(filepath + 'saved_cameras.pickle', 'rb')
		print("[INFO] Fetching saved cameras")
		cam_dict = pickle.load(f)
		f.close()

		del cam_dict[name]
		print("[INFO] " + name + " has been removed")
		f = open(filepath + 'saved_cameras.pickle', 'wb')
		pickle.dump(cam_dict, f)
		f.close()

		window.destroy()

		return





		