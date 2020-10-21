
from components import MotionDetector, Stream, CameraManager, HumanDetector2, SimilarityDetector, SimilarityDetector2, SimilarityDetector3, StorageManager

test = StorageManager(work_in_dir='../bin/storage', interval=0.1)

while(True):
    test.reduce_files()


