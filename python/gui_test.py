'''
-----------------------------------------------
title: cam_app.py
description: This app enables the user to open the stream of any network enabled IP camera. The idea is to be able to save and load
			 different cameras. At a later stage, heatmap detection and parallel streaming will be implemented
author: AF Grobler
for: Project (E) 448, Department of Electric and Electronic Engineering, University of Stellenbosch
-----------------------------------------------
'''
# imports
import tkinter
import cv2
import PIL
from PIL import Image, ImageTk
from stream import Stream
import os
import sys

# Create the Tkinter window
window = tkinter.Tk()
window.title("Skripsie 2020")

# Window variables
filepath = '../bin/'
calibrated = True
stream = ''
default_stream = Stream(src = '0', camera_brand = '')

def show_frame():
	ret, frame = default_stream.get_stream().read()
	width  = default_stream.get_stream().get(cv2.CAP_PROP_FRAME_WIDTH)  # float
	height = default_stream.get_stream().get(cv2.CAP_PROP_FRAME_HEIGHT) # float
	div_factor = 2
	if ret:
		#frame = cv2.flip(frame, 1)
		frame = cv2.resize(frame, (int(width/div_factor),int(height/div_factor)))
		cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		img = PIL.Image.fromarray(cv2image)
		imgtk = ImageTk.PhotoImage(image=img)
		video_stream.imgtk = imgtk
		video_stream.configure(image=imgtk)
		video_stream.after(10, show_frame)
		lbl_default.config(text = '')
		#cv2.imshow('Live stream', cv2image)
	else:
		lbl_default.config(text = '[ERROR] No stream to show. Please make sure that you have selected a camera to stream. If the error persists, idk.')


def updateCalibrationStatus():
	if calibrated:
		lbl_calibration_status.config(text = "Calibration status: Calibrated")
	else:
		lbl_calibration_status.config(text = "Calibration status: Not calibrated")

def list_cameras(file_path):

	cam_list = []

	if not os.path.isfile(file_path):
		print('[ERROR] The file {} is corrupted or does not exist'.format(file_path))
		return null

	with open(file_path) as fp:
		for line in fp:
			cam_list.append(line.strip().split(', '))

	return cam_list

def show_cameras():
	cam_list = list_cameras(filepath + 'saved_cameras.txt')
	cam_window = tkinter.Tk()
	cam_window.title("Select a stream")

	for cam in cam_list:
		tkinter.Button(cam_window, text=cam[0], command = lambda cam = cam[1]: update_stream(cam_window, cam)).pack()

def update_stream(window, source):
	global default_stream
	default_stream  = Stream(src = source, camera_brand = 'Foscam')
	window.destroy()


# Window elements

# Labels
lbl_calibration_status = tkinter.Label(window, text = "Calibration status: Not calibrated")
lbl_default = tkinter.Label(window, text = "Select a camera to view stream")

# Buttons
btn_select = tkinter.Button(window, text = "Select a stream", command = show_cameras)
btn_add = tkinter.Button(window, text = "Add a camera")
btn_detele = tkinter.Button(window, text = "Delete a camera")
btn_calibrate = tkinter.Button(window, text = "Calibrate system")
btn_stream = tkinter.Button(window, text = "Show stream", command = show_frame)

video_stream = tkinter.Label(window)

#Layout
btn_select.grid(row = 0, column = 0)
btn_stream.grid(row=1, column = 0)
btn_add.grid(row = 0, column = 1)
btn_detele.grid(row = 0, column = 2)
btn_calibrate.grid(row = 0, column = 3)
lbl_calibration_status.grid(row = 2, column = 0)
lbl_default.grid(row = 3, column = 0)
video_stream.grid(row = 4, column = 0)

tkinter.mainloop()


