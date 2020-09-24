import cv2
import PIL
from PIL import Image, ImageTk

class Stream:
	cap = cv2.VideoCapture()

	def __init__(self, src='0'):
		global cap
		self.src = src
		self.camera_brand = camera_brand
		self.streaming = False

		if src == '0' or src == ':@0:': #Enable webcam support
			self.cap = cv2.VideoCapture(0)
		else:
			rtsp_string = 'rtsp://' + src + '/videoMain'
			self.cap = cv2.VideoCapture(rtsp_string)

	def get_stream(self):
		#print("Source:", self.src)
		return self.cap

		