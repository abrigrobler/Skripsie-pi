from components import Stream, MotionDetector


filepath = '../bin/test_video.mov'
test_stream = Stream(filepath, test_source = True)

MD = MotionDetector(stream = test_stream, name = 'videoTest', filepath = '../bin/saved_images/', min_area = 1000)

while(True):
    if not MD.process_single_frame():
        break


