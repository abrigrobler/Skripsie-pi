
from components import MotionDetector, MotionDetector2, Stream, CameraManager, HumanDetector, SimilarityDetector, MotionDetectorLFR
import imutils
import cv2

filepath = '../bin/saved_images/'
min_area = 1000

MD = MotionDetectorLFR(stream = Stream(src = 's_cam:skripsie_cam@10.10.10.101:88/videoMain', test_source = False), name = 'LFR_test', min_area = min_area, filepath = filepath)
#SD = SimilarityDetector(stream = Stream(src = 's_cam:skripsie_cam@10.10.10.101:88/videoMain', test_source = False), name = 'first_sim_test', filepath = filepath)

while(True):
	MD.process_single_frame()
	'''
	f = SD.process_frame()
	if f is None:
		continue
	p, c = f
	p = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
	c = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
	p = imutils.resize(p, width=800)
	c = imutils.resize(c, width=800)
	cv2.imshow('Prev', cv2.subtract(p,c))
	#cv2.imshow('Current', c)

	key = cv2.waitKey(1) & 0xFF
	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break
	'''


'''
cam_list = CameraManager.list_cameras('../bin/')

MD_list = []

for cam in cam_list:
	S = Stream(src = cam[1])
	MD_list.append(MotionDetector(stream = S, name = cam[0], min_area = min_area, filepath = filepath))

while(True):
	for md in MD_list:
		md.process_single_frame()
'''