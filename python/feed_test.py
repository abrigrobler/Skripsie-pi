
from components import MotionDetector, Stream, CameraManager, HumanDetector

test = HumanDetector(work_in_dir = '../bin/saved_images', interval = 0.5)

while(True):
	test.detect_and_filter()