
from components import MotionDetector, Stream, CameraManager, HumanDetector, SimilarityDetector, SimilarityDetector2, SimilarityDetector3

test = SimilarityDetector2(work_in_dir = '../bin/saved_images', interval = 60)

while(True):
	test.match_and_filter()