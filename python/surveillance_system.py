from components_reduced import CameraManager, StorageManager, SystemMotionDetection, SystemFiltering
from threading import Thread

SM = StorageManager(work_in_dir='../bin/storage', interval=3, space = 5, critical_space=2)

def clean_storage():
    while True:
        SM.reduce_files()

def detection():
    SystemMotionDetection.start()
def filtering():
    SystemFiltering.start(filter_interval=1)
    
MD_THREAD = Thread(target = detection)
MD_THREAD.start()

FILTERING_THREAD = Thread(target=filtering)    
FILTERING_THREAD.daemon = True
FILTERING_THREAD.start()

STORAGE_THREAD = Thread(target=clean_storage)
STORAGE_THREAD.daemon = True
STORAGE_THREAD.start()



