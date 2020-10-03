
from components import MotionDetector, MotionDetector2, Stream, CameraManager, HumanDetector

filepath = '../bin/saved_images/'
min_area = 500

MD = MotionDetector2(stream = Stream(src = 's_cam:skripsie_cam@10.10.10.101:88/videoMain', test_source = False), name = 'long_test', min_area = min_area, filepath = filepath)

while(True):
	MD.process_single_frame()


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