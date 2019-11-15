import json
import base64
import numpy as np
import cv2
from PIL import Image

def save(value, w, h, name):
	img_bytes = base64.decodebytes(value.encode('utf-8'))
	img = Image.frombytes('RGB', (h, w), img_bytes, 'raw')
	img.save(name)

json_file = open('result.json', encoding='utf-8')
json_data = json.load(json_file)
json_file.close()

w = json_data['w']
h = json_data['h']

save(json_data['image'], w, h, 'rotated.png')