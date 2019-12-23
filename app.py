import numpy as np
import cv2
from PIL import Image
import math
import os

from flask import Flask
from flask import request, send_file, redirect, url_for, send_from_directory
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

from scan_rotator import ScanRotator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

scan_rotator = ScanRotator()

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in set([ 'jpg', 'png', 'bmp', 'jpeg'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			img, angle = scan_rotator.auto_rotate(np.array(Image.open(file)))
			cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_' + filename), img)

			# return redirect(url_for('uploaded_file', filename='rotated_' + filename))
			return redirect(url_for('result', filename=filename))

	return '''
	<!doctype HTML>
	<title>Upload file</title>
	<h1>Upload new file</h1>
	<form action="" method=post enctype=multipart/form-data>
		<p>
			<input type=file name=file>
			<input type=submit value=Upload>
		</p>
	</form>
	</html>
	'''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/result/<filename>')
def result(filename):
	return '''
	<!doctype HTML>
	<title>Upload file</title>
	<a href='/uploads/{filename}' target='_blank'><img src='/uploads/{filename}' width=48% height=auto></a>
	<a href='/uploads/rotated_{filename}' target='_blank'><img src='/uploads/rotated_{filename}' width=48% height=auto></a>
	</html>
	'''.format(filename=filename)

# def get(self):
# 	return "Working"

# def post(self):
# 	img = np.array(Image.open(request.files['img']))
# 	rotated_img, angle = self.scan_rotator.auto_rotate(img)

	# rot_bytes = base64.b64encode(rotated_img).decode('utf-8')

	# return { 
	# 	"image" : rot_bytes,
	# 	"w" : rotated_img.shape[0],
	# 	"h" : rotated_img.shape[1],
	# 	"angle" : angle
	# }	    	


# api = Api(app)

# api.add_resource(DocRotator, '/')

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')

# curl -F "img=@/home/andrew/Desktop/images/1_rot.png" http://localhost:5000 > out.json