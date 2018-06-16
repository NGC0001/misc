#!/usr/bin/python3
# -*- coding: utf-8 -*-
# A simple Flask script, with the ability to recieve uploaded file.

import os
import cv2
import numpy as np
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'bmp', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


basic_html = '''
<!doctype html>
<title>Flask</title>
<h1>Please Upload Two Images</h1>
<form method=post enctype=multipart/form-data>
    <input type=file name=file1>
    <input type=file name=file2>
    <input type=submit value=Upload>
</form>
'''

display = '''
<p>
    <img style='width:30%;padding:0.2%;border:medium outset;' src='PLACE_HOLDER_1' />
    <img style='width:30%;padding:0.2%;border:medium outset;' src='PLACE_HOLDER_2' />
    <img style='width:30%;padding:0.2%;border:medium outset;' src='PLACE_HOLDER_3' />
</p>
'''


def compose(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    height, width, channels = img1.shape
    img2 = cv2.resize(img2, (width, height))
    img3 = img2 / 2 + img1 / 2
    return img3.astype(np.uint8)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file1' in request.files and 'file2' in request.files:
            file1 = request.files['file1']
            file2 = request.files['file2']
            if (file1 and file1.filename != '' and allowed_file(file1.filename)
                    and file2 and file2.filename != '' and allowed_file(file2.filename)):
                file1name = secure_filename(file1.filename)
                file2name = secure_filename(file2.filename)
                file1path = os.path.join(app.config['UPLOAD_FOLDER'], file1name)
                file2path = os.path.join(app.config['UPLOAD_FOLDER'], file2name)
                file1.save(file1path)
                file2.save(file2path)
                img3 = compose(file1path, file2path)
                file3name = file1name.rsplit('.', 1)[0] + '_' + file2name.rsplit('.', 1)[0] + '.jpg'
                file3path = os.path.join(app.config['UPLOAD_FOLDER'], file3name)
                cv2.imwrite(file3path, img3)
                return basic_html + display.replace(
                        'PLACE_HOLDER_1', url_for('uploaded_file', filename=file1name)).replace(
                        'PLACE_HOLDER_2', url_for('uploaded_file', filename=file2name)).replace(
                        'PLACE_HOLDER_3', url_for('uploaded_file', filename=file3name))
        return redirect(request.url)
    return basic_html
    


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
