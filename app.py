import matplotlib.pyplot as plt
import tempfile
from urllib.request import urlopen
from six import BytesIO
from PIL import Image
from PIL import ImageOps
import time

# For Flask app
from flask import Flask, flash, jsonify, request, redirect, render_template
from flask_cors import CORS
import base64
from io import BytesIO


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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
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
        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', image_base64=encoded_string)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/api/estimate', methods=['POST'])
def classify():
    time.sleep(10)
    print("called...")
    data = request.get_json()
    img = data['image_b64']
    classified_img = img
    return jsonify({'classified_b64': classified_img})

if __name__ == "__main__":
    app.run()