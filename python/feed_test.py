import cv2
import numpy as np
import imutils

vid = cv2.VideoCapture('rtsp://admin:admin@10.10.10.158:554/11')
#vid2 = cv2.VideoCapture(0)

while(True):
	ret, img = vid.read()
	#ret2, img2 = vid2.read()


	img = imutils.resize(img, width=900)
	#img2 = imutils.resize(img2, width = 900)
	cv2.imshow('Foscam_01', img)
	#cv2.imshow('webcam', img2)
	#print("[WARNING] Feed not available")

	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
vid.stop() if args.get("video", None) is None else vid.release()
cv2.destroyAllWindows()