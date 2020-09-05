'''
-----------------------------------------------
title: cam_app.py
description: This command line app enables the user to open the stream of any network enabled IP camera. The idea is to be able to save and load
			 different cameras. At a later stage, heatmap detection and parallel streaming will be implemented
author: AF Grobler
for: Project (E) 448, Department of Electric and Electronic Engineering, University of Stellenbosch
-----------------------------------------------
'''

import cv2
import numpy
import imutils
import os
import sys

# Functions

# The cameras need to be listed when requested by the user

def list_cameras(file_path):

	cam_list = []

	if not os.path.isfile(file_path):
		print('[ERROR] The file {} is corrupted or does not exist'.format(file_path))
		return null

	with open(file_path) as fp:
		for line in fp:
			cam_list.append(line.strip().split(', '))

	return cam_list

# Once a camera is chosen, open the stream of that camera until 'q' is pressed

def open_stream(ip):

	print('[INFO] Press \'q\' to exit streaming')

	rtsp_string = 'rtsp://' + ip + '/videoMain'

	try:
		vid = cv2.VideoCapture(rtsp_string)
	except:
		print('[ERROR] Could not connect to IP camera. Please ensure that you enter the required information correctly')


	while(True):
		ret, img = vid.read()

		if ret:

			img = imutils.resize(img, width=900)
			cv2.imshow('Foscam_01', img)
			#print("[WARNING] Feed not available")
		else:
			break
			print('[ERROR] Stream not available')

		key = cv2.waitKey(1) & 0xFF
		# if the `q` key is pressed, break from the loop
		if key == ord("q"):
			print('[INFO] Stream ended.')
			cv2.destroyAllWindows()
			break
		

	# cleanup the camera and close any open windows


# Functional Code

filepath = '../bin/'

stream = ''


print("\nIP Camera streaming command line app.\n")

while(True):
	choice = str(input("Please select one of the following:\nN - Set up a new camera\nL - List existing cameras\nQ - Exit the program\n"))

	if choice == 'N':

		print("You have chosen to set up a new camera. This camera will automatically be saved. Please provide:\n")
		cam_name = input("Camera name: ")
		cam_ip = input("Camera IP and port: ")
		cam_user = input("Username: ")
		cam_pass = input("Password: ")

		stream = cam_user + ':' + cam_pass + '@' + cam_ip

		with open(filepath + "saved_cameras.txt", "a") as cam_file:
			cam_file.write(cam_name + ', ' + cam_user + ':' + cam_pass + '@' + cam_ip + '\n')

		open_stream(stream)

	elif choice == 'L':

		print("You have chosen to load an existing camera.")
		cam_list = list_cameras(filepath + 'saved_cameras.txt')

		count = 1

		for cam in cam_list:
			print(str(count) + '. Camera name: ' + cam[0] + ' Stream: ' + cam[1] + '\n')
			count = count + 1

		selected_cam = int(input("\nPlease select a camera to view from the list above: ")) - 1
		stream = cam_list[selected_cam][1]

		open_stream(stream)

	elif choice == 'Q':
		sys.exit()

	else:
		print("Invalid option")











