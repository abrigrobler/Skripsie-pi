import components
from threading import Thread

class System:
    '''
    The System class now finally makes use of all the components, to create a fully functional, automated system
    '''
    
    MD_THREAD: Thread
    BG_THREAD: Thread
    
    def __init__(self, streams_dir, storage_dir, working_dir, required_space, critical_space, filter_interval, clean_interval):
        self.streams_dir = streams_dir
        self.storage_dir = storage_dir
        self.working_dir = working_dir
        self.required_space = required_space
        self.critical_space = critical_space
        self.filter_interval = filter_interval
        self.clean_interval = clean_interval
        
        self.sim_detector = components.SimilarityDetector2(work_in_dir = self.working_dir, interval = self.filter_interval, similarity_thresh=93)
        self.storage_cleaner = components.StorageManager(work_in_dir = self.working_dir, interval = self.clean_interval, space = self.required_space, critical_space=self.critical_space)
        
        self.cam_manager = components.CameraManager()
        
        self.stream_list = self.cam_manager.list_cameras()
        
        self.m_detectors = []
        for s in self.stream_list:
            self.m_detectors.append(components.MotionDetectorLFR(components.Stream(s[1]), name = s[0], min_area = 1000, filepath = self.working_dir)
    
    def detect_motion_on_streams(self):
        while True:
            for d in self.m_detectors:
                d.process_single_frame()
    
    def filter_and_optimise_storage(self):
        while True:
            self.sim_detector.match_and_filter()
            self.storage_cleaner.reduce_files()
        
    def run(self):
        self.MD_THREAD = Thread(target = self.detect_motion_on_streams)
        self.BG_THREAD = Thread(target = self.filter_and_optimise_storage)
        
        self.MD_THREAD.start()
        self.BG_THREAD.start()
        
sys = System(streams_dir='../bin/', storage_dir='../bin/storage/', working_dir='../bin/saved_images/',required_space=5, critical_space=1, filter_interval=10, clean_interval=20)
sys.run()
        
        
        