# Initial classification model using TesorFlow's AlexNet (Not used in the end)
# -*- coding: utf-8 -*-
"""model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13sCsL7yzYs4TaewgtyxmXfSdMbn4P0f6

Classification using TesorFlow's AlexNet for CNN
"""

# import statements
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import numpy as np

# check TensorFlow version
print(tf.__version__)

# load test image
image_path = "./testImage.png"
Image.open(image_path)

# convert png to tensor
def convert_png_to_tensor(image_path):
  img = open(image_path, 'rb').read()
  img_tensor = tf.image.decode_png(img)
  return img_tensor

img_tensor = convert_png_to_tensor(image_path)
print("Shape of image:",img_tensor.shape, "\n")
img_tensor
# convert_tensor = transforms.ToTensor()
# imgTensor = convert_tensor(imagePng)
# print("Shape of image: {}".format(imgTensor.shape))
# imgTensor

# resize images to (277, 277, 3) - AlexNet uses this size as input
def resize_image(image):
    # Normalize images to have a mean of 0 and standard deviation of 1
    image = tf.image.per_image_standardization(image)
    image = tf.image.resize(image, (227,227))
    return image

img_resized = resize_image(img_tensor)

print("Shape of image: {}".format(img_resized.shape))
img_resized

# create train_img, train_label
# currently there is only 1 image for testing

train_img = np.array([img_resized])
print("Size of training set: {}".format(train_img.shape))
train_label = np.array([[0]])

# generate dataset for training, validation and testing
train_ds = tf.data.Dataset.from_tensor_slices((train_img, train_label))
train_ds = train_ds.batch(batch_size=1, drop_remainder=True)

# To be added
# test_ds = tf.data.Dataset.from_tensor_slices((test_images, test_labels))
# validation_ds = tf.data.Dataset.from_tensor_slices((validation_images, validation_labels))

# (AlexNet architecture code snippet referenced from https://towardsdatascience.com/implementing-alexnet-cnn-architecture-using-tensorflow-2-0-and-keras-2113e090ad98)
# Model - parameters can be tuned
model = keras.models.Sequential([
    keras.layers.Conv2D(filters=96, kernel_size=(11,11), strides=(4,4), activation='relu', input_shape=(227,227,3)),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Conv2D(filters=256, kernel_size=(5,5), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(filters=384, kernel_size=(3,3), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.Conv2D(filters=256, kernel_size=(3,3), strides=(1,1), activation='relu', padding="same"),
    keras.layers.BatchNormalization(),
    keras.layers.MaxPool2D(pool_size=(3,3), strides=(2,2)),
    keras.layers.Flatten(),
    keras.layers.Dense(4096, activation='relu'),
    keras.layers.Dropout(0.8),
    keras.layers.Dense(4096, activation='relu'),
    keras.layers.Dropout(0.8),
    keras.layers.Dense(10, activation='softmax')
])

# using cross-entrophy as loss function, stochastic gradient descent with learning rate of 0.001 as optimizer
# feel free to tune learning rate
model.compile(optimizer=tf.optimizers.SGD(lr=0.05), loss='categorical_crossentropy')
model.summary()

# check type
train_ds

# train model
model.fit(train_ds)