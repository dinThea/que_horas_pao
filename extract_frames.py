import cv2
from imutils import contours
import imutils
import os
from src.Digit import Digit
from src.operations import ThreshImage
import json

class TempFrameFinder:
	
	def __init__(self, video_path, finder, image_filter, interest_area=(91,121, 1126,1194)):
		self._finder = finder
		self._finder.gather_digits()
		self._image_filter = image_filter
		self._video_path = video_path
		self._frame_dict = {}
		self._interest_area = interest_area

	def _open_video(self):
		self.cap = cv2.VideoCapture(self._video_path)
	
	def _get_interest_area(self, frame):
		image = frame[self._interest_area[0]:self._interest_area[1], self._interest_area[2]:self._interest_area[3]]
		image = imutils.resize(image, height=500)
		return image

	def _find_contours(self, t_image):
		cnts = cv2.findContours(t_image.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)

		digitCnts = []
		for c in cnts:
			digitCnts.append(c)
		digitCnts = contours.sort_contours(digitCnts,
			method="left-to-right")[0]
		
		return digitCnts

	def _find_number_string(self, thresh, cnts):
		number = ''
		for i, c in enumerate(cnts):
			(x, y, w, h) = cv2.boundingRect(c)
			to_compare = thresh[y:y+h, x:x+w]
			digit = self._finder.get_digit(to_compare)

			if digit == 11:
				number += '-'
			elif digit == 10:
				number += '.'
			else:
				number += str(digit)
		return number

	def process(self):

		self._open_video()
		# load the input image and grab the image dimensions
		frame = 2000
		temp = ''
		begin = 2000
		last_temp = ''
		self.cap.set(cv2.CAP_PROP_POS_FRAMES, 2000)
		total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
		while self.cap.isOpened():
			try:
				_, image = self.cap.read()
				image = self._get_interest_area(image)
				thresh = self._image_filter.thresh(image)
				digitCnts = self._find_contours(thresh)

				number = self._find_number_string(thresh, digitCnts)

				if '..' not in number and '--' not in number and number != '.': 
					if number not in self._frame_dict:
						self._frame_dict[number] = {}
					if number != temp:
						if temp in self._frame_dict:
							self._frame_dict[temp][begin] = frame 
						self._frame_dict[number][frame] = frame
						temp = number
						begin = frame
				frame += 100
				self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
				print (frame/total_frames, number)
			except TypeError as e:
				print (e)
				break

		with open('result.json', 'w') as result:
			result.write(json.dumps(self._frame_dict))
		print (self._frame_dict)

if __name__ == '__main__':
	finder = TempFrameFinder('bread.mp4', Digit(ThreshImage()), ThreshImage())
	finder.process()