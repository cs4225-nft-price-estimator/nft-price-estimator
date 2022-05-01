import math
import os
import numpy as np
import time

# For Flask app
from flask import Flask, flash, jsonify, request, redirect, render_template
from flask_cors import CORS
import base64

# For Machine Learning Model
import pickle
from sklearn.svm import SVR
import tensorflow as tf
from keras.preprocessing import image
from keras.applications.resnet_v2 import ResNet50V2, preprocess_input

app = Flask(__name__)
CORS(app)

rootdir = os.getcwd()
UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Model and config
model = ResNet50V2(weights="imagenet", include_top=False)
FLATTENED_LENGTH = 100352

@app.route('/api/estimate', methods=['POST'])
def classify():
    time.sleep(1) # Loading effect
    data = request.get_json()
    img_base64 = data['image_b64']
    base64_img_bytes = img_base64.encode('utf-8')
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'target_img.png')
    with open(path, 'wb') as file_to_save:
        decoded_image_data = base64.decodebytes(base64_img_bytes)
        file_to_save.write(decoded_image_data)
    try:
        img = image.load_img(path, target_size=(224, 224))
    except Exception as e: 
        flash('Error laoding image: {}'.format(e))
        return redirect(request.url)
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    try: 
        filename = '{}/nft_estimator_model.sav'.format(rootdir)
        nft_model: SVR = pickle.load(open(filename, 'rb'))
        features = model.predict(img_array)
        feature = features[0].flatten()[:FLATTENED_LENGTH]
        feature_arr = feature.reshape(1,FLATTENED_LENGTH)
        result = nft_model.predict(feature_arr)
        estimated_price = str(math.exp(result[0]))
        print('Price in eth = {}'.format(estimated_price))
        return jsonify({'classified_b64': img_base64, 'price': estimated_price})
    except Exception as e:
        print('Error loading model, error = {}'.format(e))   
    return jsonify({'classified_b64': img_base64, 'price': "-1"})

if __name__ == "__main__":
    app.run(debug=True)