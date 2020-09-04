import cv2
import numpy as np
import imutils

print("[INFO] This script allows you to stream live video from an IP camera using RTSP. Please provide the following:")

cam_ip = input("Camera IP Address: ")
cap_port = input("Camera Port: ")
username = input("Username: ")
password = input("Password: ")

rtsp_string = 'rtsp://' + username + ':' + password + '@' + cam_ip + ':' + cap_port + '/videoMain'

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
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		print('[INFO] Stream ended.')
		break
		

# cleanup the camera and close any open windows
cv2.destroyAllWindows()