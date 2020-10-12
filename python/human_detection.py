
from components import MotionDetector, Stream, CameraManager, HumanDetector, SimilarityDetector2, SimilarityDetector3

test = HumanDetector(work_in_dir = '../bin/saved_images', interval = 60)

while(True):
	test.detect_and_filter()