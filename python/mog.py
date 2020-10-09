#Virtual environment named 'env'
#Apparently a venv is required to actually use OpenCV... Why?

# import the necessary packages
from imutils.video import VideoStream
from components import Stream
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np

stream = Stream(src = 's_cam:skripsie_cam@10.10.10.101:88/videoMain', test_source = False)
min_area = 750

fg_detect = cv2.createBackgroundSubtractorKNN()

#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

while(True):

	frame = frame_orig = stream.get_stream()


	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if frame is None:
		continue

	text = "Not Detected"
		
	#frame = np.fliplr(frame)
	frame = imutils.resize(frame, width=800)
	fg_mask = fg_detect.apply(frame)

	#fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel) #Remove noise
	fg_mask = cv2.medianBlur(fg_mask, 21q)

	cnts = cv2.findContours(fg_mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < min_area:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text

		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Detected"

		#img_name = 'saved_images/' + datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p") + '.jpg'
		#cv2.imwrite(img_name, frame) #Saving

	# draw the text and timestamp on the frame
	cv2.putText(frame, "Motion: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Frame Delta", fg_mask)
	cv2.imshow("Security Feed", frame)

	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows

cv2.destroyAllWindows()

