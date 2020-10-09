
from components import MotionDetector, Stream, CameraManager, HumanDetector, SimilarityDetector2

test = SimilarityDetector2(work_in_dir = '../bin/saved_images', interval = 2)

while(True):
	test.match_and_filter()