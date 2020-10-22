
from components import MotionDetector, MotionDetector2, Stream, CameraManager, HumanDetector, SimilarityDetector, MotionDetectorLFR
import imutils
import cv2

filepath = '../bin/Zosi_01/'
min_area = 1000

MD_list = []
cam_list = CameraManager.list_cameras('../bin/')
for c in cam_list:
    MD_list.append(MotionDetectorLFR(stream=Stream(
        c[1]), name=c[0], min_area=min_area, filepath=str('../bin/' + c[0])))
# MD = MotionDetectorLFR(stream = Stream(src = 'admin:admin@10.10.10.159:554/11', test_source = False), name = 'Zosi_01', min_area = min_area, filepath = filepath)
# SD = SimilarityDetector(stream = Stream(src = 's_cam:skripsie_cam@10.10.10.101:88/videoMain', test_source = False), name = 'first_sim_test', filepath = filepath)

while(True):
    for MD in MD_list:
        MD.process_single_frame()
