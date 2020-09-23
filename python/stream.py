import cv2
import PIL
from PIL import Image, ImageTk

class Stream:

	def __init__(self, src='0', camera_brand=''):
		self.src = src
		self.camera_brand = camera_brand
		self.streaming = False

		if src == '0':
			self.cap = cv2.VideoCapture(0)
		else:
			if camera_brand == 'Foscam':
				rtsp_string = 'rtsp://' + src + '/videoMain'
				self.cap = cv2.VideoCapture(rtsp_string)
			else:
				print("[ERROR] Please provide a brand")

	def get_stream(self):
		#print("Source:", self.src)
		return self.cap

		