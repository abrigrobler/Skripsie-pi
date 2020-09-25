
from components import MotionDetector, Stream, CameraManager

filepath = '../bin/saved_images/'
src = '0'
name = 'Webcam'
min_area = 3000

cam_list = CameraManager.list_cameras('../bin/')

MD_list = []

for cam in cam_list:
	S = Stream(src = cam[1])
	MD_list.append(MotionDetector(stream = S, name = cam[0], min_area = min_area, filepath = filepath))

while(True):
	for md in MD_list:
		md.process_single_frame()
