import cv2
import PIL
from PIL import Image, ImageTk

class Stream:

	def __init__(self, src=0, width=400, height=300):
		self.streaming = False
		self.cap = cv2.VideoCapture(src)
		self.width, self.height = width, height

		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

	def get_stream(self):
		return self.cap

		