import numpy as np
import cv2
from PIL import Image
import math
import base64
import json

from flask import Flask
from flask import request
from flask_restful import Resource, Api

class DocRotator(Resource):
	def __init__(self):
		self.verbose = 0

		self.min_canny = 50
		self.max_canny = 200
		self.min_lines_count = 5 # минимальное число линий для поиска

	# вращение изображения image на угол angle
	def rotate_image(self, image, angle):
		image_center = tuple(np.array(image.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

	# получение прямых
	def detect_lines(self, image):
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # переводим в оттенки серого
		edges = cv2.Canny(gray, self.min_canny, self.max_canny, apertureSize=3) # выделяем границы

		min_line_length = min(image.shape[0], image.shape[1]) / 4
		max_line_gap = 15

		while max_line_gap < 200:
			lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 200, minLineLength=min_line_length, maxLineGap=max_line_gap)

			if not (lines is None) and (len(lines) > self.min_lines_count):
				break

			max_line_gap += 10

			if self.verbose:
				print('INFO: maxLineGap:', max_line_gap)

		vert_lines = []
		horiz_lines = []

		for line in lines:
			for x1,y1,x2,y2 in line:
				dy = abs(y1 - y2)
				dx = abs(x1 - x2)

				if dx < dy:
					vert_lines.append((x1, y1, x2, y2))
				else:
					horiz_lines.append((x1, y1, x2, y2))
		
		if self.verbose:
			print('vert_lines:', len(vert_lines), 'horiz_lines: ', len(horiz_lines), end='')

		return lines, vert_lines, horiz_lines

	# выбор угла поворота на основе прямых
	def select_angle(self, lines):
		angle = 0

		for x1, y1, x2, y2 in lines:
			angle += math.atan2(y2 - y1, x2 - x1)

		return angle / len(lines)

	# получение картинки с линиями
	def get_image_with_lines(self, shape, horiz_lines, vert_lines):
		img_lines = np.zeros(shape)

		for x1, y1, x2, y2 in horiz_lines:
			cv2.line(img_lines, (x1, y1), (x2, y2), (255, 0, 0), 2)

		for x1, y1, x2, y2 in vert_lines:
			cv2.line(img_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)

		return img_lines

	# автоматический поворот изображения image
	def auto_rotate(self, image):
		lines, vert_lines, horiz_lines = self.detect_lines(image)
		angle = self.select_angle(horiz_lines)
		rotated = self.rotate_image(image, angle / math.pi * 180)

		return rotated, angle

	def get(self):
		return "Working"

	def post(self):
	    img = np.array(Image.open(request.files['img']))
	    rotated_img, angle = self.auto_rotate(img)

	    rot_bytes = base64.b64encode(rotated_img).decode('utf-8')

	    return { 
	    	"image" : rot_bytes,
	    	"w" : rotated_img.shape[0],
	    	"h" : rotated_img.shape[1],
	    	"angle" : angle
	    }	    	

app = Flask(__name__)
api = Api(app)

api.add_resource(DocRotator, '/')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')