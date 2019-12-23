from typing import List, Tuple
import cv2
import numpy as np
import math

class ScanRotator():
	"""
		класс для автоматического выравнивания сканов
	"""
	def __init__(self):
		self.verbose = 0  # flag for debugging
		self.min_canny = 50  # min threshold for edge detection
		self.max_canny = 200  # max threshold for edge detection
		self.min_lines_count = 5  # minimum number of lines for search

	def _rotate_image(self, image: np.ndarray, angle: float):
		"""
			function for rotating image by angle
		"""
		image_center = tuple(np.array(image.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		return cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

	def _split_lines(self, lines: List[Tuple[float, float, float, float]]) -> Tuple[List, List]:
		"""
			function for splitting lines by horizontal and vertical
		"""
		vert_lines = []
		horiz_lines = []

		for line in lines:
			for x1, y1, x2, y2 in line:
				dy = abs(y1 - y2)
				dx = abs(x1 - x2)

				if dx < dy:
					vert_lines.append((x1, y1, x2, y2))
				else:
					horiz_lines.append((x1, y1, x2, y2))

		return vert_lines, horiz_lines

	def _detect_lines(self, image: np.ndarray) -> Tuple[List, List, List]:
		"""
			function for getting lines on image
		"""
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale
		edges = cv2.Canny(gray, self.min_canny, self.max_canny, apertureSize=3)  # edge detection

		min_line_length = min(image.shape[0], image.shape[1]) / 4
		max_line_gap = 15

		while max_line_gap < 200:
			lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 200, minLineLength=min_line_length, maxLineGap=max_line_gap)

			if lines is not None and (len(lines) > self.min_lines_count):
				break

			max_line_gap += 10

			if self.verbose:
				print('INFO: maxLineGap:', max_line_gap)

		vert_lines, horiz_lines = self._split_lines(lines)
		
		if self.verbose:
			print('vert_lines:', len(vert_lines), 'horiz_lines: ', len(horiz_lines), end='')

		return lines, vert_lines, horiz_lines

	def _select_angle(self, lines: List[Tuple[float, float, float, float]]) -> float:
		"""
			function for selecting angle of scan rotating from lines
		"""
		if len(lines) == 0:
			return 0

		angle = 0

		for x1, y1, x2, y2 in lines:
			angle += math.atan2(y2 - y1, x2 - x1)

		return angle / len(lines)

	def auto_rotate(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
		"""
			automatic rotation of one image
		"""
		lines, vert_lines, horiz_lines = self._detect_lines(image)
		angle = self._select_angle(horiz_lines)
		rotated = self._rotate_image(image, angle / math.pi * 180)

		return rotated, angle    	

	def rotate(self, images: List[np.ndarray]) -> List[np.ndarray]:
		"""
			automatic rotation of list of images
		"""
		rotated = []

		for img in images:
			res, angle = self.auto_rotate(img)
			rotated.append(res)

		return rotated