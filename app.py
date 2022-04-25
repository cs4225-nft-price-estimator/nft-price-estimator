import math
import os
import matplotlib.pyplot as plt
import tempfile
from urllib.request import urlopen
import numpy as np
from six import BytesIO
from PIL import Image
from PIL import ImageOps
import time

# For Flask app
from flask import Flask, flash, jsonify, request, redirect, render_template
from flask_cors import CORS
import base64
from io import BytesIO

# For Model
# import pandas
# from sklearn import model_selection
import pickle
from sklearn.svm import SVR
from PIL import Image
import tensorflow as tf
from keras.preprocessing import image
# from keras.applications.vgg16 import VGG16, preprocess_input
from keras.applications.resnet_v2 import ResNet50V2, preprocess_input

def display_image(image):
  fig = plt.figure(figsize=(20, 15))
  plt.grid(False)
  plt.imshow(image)


def download_and_resize_image(url, new_width=256, new_height=256,
                              display=False):
  _, filename = tempfile.mkstemp(suffix=".jpg")
  response = urlopen(url)
  image_data = response.read()
  image_data = BytesIO(image_data)
  pil_image = Image.open(image_data)
  pil_image = ImageOps.fit(pil_image, (new_width, new_height), Image.ANTIALIAS)
  pil_image_rgb = pil_image.convert("RGB")
  pil_image_rgb.save(filename, format="JPEG", quality=90)
  print("Image downloaded to %s." % filename)
  if display:
    display_image(pil_image)
  return filename

app = Flask(__name__)
CORS(app)
 
UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_default_img():
    with open('img.txt') as f:
        lines = f.readlines()
        return lines[0]

@app.route('/')
def home():
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        encoded_string = base64.b64encode(file.read())
        encoded_string = encoded_string.decode('utf-8')
        flash('Image successfully uploaded and displayed.')
        return render_template('index.html', image_base64=encoded_string)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

# model = VGG16(weights="imagenet", include_top=False)
model = ResNet50V2(weights="imagenet", include_top=False)

@app.route('/api/estimate', methods=['POST'])
def classify():
    print("called... wait 2 seconds to add loading effect")
    time.sleep(2)
    data = request.get_json()
    img_base64 = data['image_b64']
    print('Type of img = {}'.format(type(img_base64)))
    base64_img_bytes = img_base64.encode('utf-8')
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'target_img.png')
    with open(path, 'wb') as file_to_save:
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        file_to_save.write(decoded_image_data)
    try:
        img = image.load_img(path, target_size=(224, 224))
    except Exception as e: 
        print('Error loading image: {}'.format(e))
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    try:
        # filename = 'nft_estimator_model.sav'
        filename = 'nft_estimator_model_SVR_5K.sav'
        # nft_model: LinearRegression = pickle.load(open(filename, 'rb'))
        nft_model: SVR = pickle.load(open(filename, 'rb'))
        features = model.predict(img_array)
        # feature = features[0].flatten()[:25088]
        # feature_arr = feature.reshape(1,25088)
        feature = features[0].flatten()[:100352]
        feature_arr = feature.reshape(1,100352)
        result = nft_model.predict(feature_arr)
        estimated_price = str(3 * math.exp(result[0]))
        print('Price in eth = {}'.format(estimated_price))
        return jsonify({'classified_b64': img_base64, 'price': estimated_price})
    except Exception as e:
        print('Error loading model, error = {}'.format(e))   
    return jsonify({'classified_b64': img_base64, 'price': "-1"})

if __name__ == "__main__":
    app.run(debug=True)