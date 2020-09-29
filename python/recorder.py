from components import Stream, MotionDetector


filepath = '../bin/test_video.mov'
test_stream = Stream(filepath, test_source = True)

MD_list = []

for i in range(3):
    
    MD_list.append(MotionDetector(stream = test_stream, name = 'videoTest', filepath = '../bin/saved_images/', min_area = 1000))
while(True):
    for md in MD_list:
        if not md.process_single_frame():
            break


