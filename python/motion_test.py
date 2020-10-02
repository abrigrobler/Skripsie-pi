
from components import MotionDetector, Stream, CameraManager

filepath = '../bin/saved_images/'
src = '0'
name = 'Webcam'
min_area = 2000

MD = MotionDetector(stream = Stream(src = '../bin/test_video.mov', test_source = True), name = 'test_video', min_area = min_area, filepath = filepath)

while(True):
	if not MD.process_single_frame():
		print("Video finished")
		break

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