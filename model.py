import os
import math
import time
import numpy as np
import shutil
#Reading the training images from the path and labelling them into the given categories
import numpy as np
from PIL import Image
from numpy import asarray
import pandas as pd
import glob
import matplotlib.pyplot as plt
# import cv2 # this is an important module to get imported which may even cause issues while reading the data if not used
import os
import seaborn as sns # for data visualization 
import tensorflow as tf
# import keras
import json
from PIL import Image
from keras.preprocessing import image
# from tensorflow.python.keras.applications.vgg16 import preprocess_input
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.svm import SVR
from keras.applications.resnet_v2 import ResNet50V2, preprocess_input
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVR
from sklearn.kernel_approximation import Nystroem

rootdir = os.getcwd() 
metadatadir = rootdir + '/scraped_api_collections'
imagedir = rootdir + '/scraped_images'
metadataList = os.listdir(metadatadir)
all_collections = []
for f in metadataList:
    if '.json' in f and '.amltmp' not in f:
        collection = f[:-5]
        all_collections.append(collection) 
print(f'Total number of collections: {len(all_collections)}')

collections_to_exclude = ['cryptopunks', 'coolpetsnft', 'beanzofficial', 'akutar-mint-pass', 'veefriends-series-2', 'worldwidewebbland', 'quantum-access-pass',
 '0xogpass', 'art-blocks', 'bff-friendship-bracelets', 'baosociety-official', 'ghxsts-comics', 'gutter-juice', 'coniun-pass', 'the-seekers', 'cyberronin-haruka',
 'firstdayout', 'dennisrodmansbarbershopmint', 'huxley-comics', 'sunmiya-club-official', 'mirandus', 'the-meta-kongz', 'space-boo-official-nft', 'chromie-squiggle-by-snowfro',
 'clonex-mintvial', 'syltare-dawn-of-east-klaytn', 'yakuza-pandas', 'retro-arcade-collection', 'lasercat-nft', 'town-star', 'shinsekai-portal', 'the-artieverse', 
 'project-godjira-gen-2', 'officialkenkyo', 'mv3-access-passes', 'antebellumgenesisland']
print(f'Number of collections to exclude: {len(collections_to_exclude)}')

collections = [c for c in all_collections if c not in collections_to_exclude] 
print(f'Number of collections to train: {len(collections)}')
print(collections)


cnn_model = ResNet50V2(weights="imagenet", include_top=False)

# read metadata and form data with labels
# data is CNN feature vector
# label is price

NUM_IMAGES = 20
# collections = ['10ktf-stockroom', 'acrocalypse', 'alienfrensnft', 'bobutoken', 'bossbeauties', 'cyberkongz', 'forgottenruneswizardscult', 'gnssart', 'headtripz'] # small collections to test
data = []
cnn_start = time.time()

for collection in collections:
  count = 0
  metadata_file = open(os.path.join(metadatadir, collection + '.json'))
  for metadata in metadata_file:
    try:
      metadata_json = json.loads(metadata)
      # get price and image
      price = metadata_json['price']
      price = math.log(metadata_json['price'])
      id = str(metadata_json['id'])
      img_path = os.path.join(imagedir, collection, collection + '-#' + id + '.png')
      # img = image.load_img(img_path, target_size=(299, 299))
      img = image.load_img(img_path, target_size=(224, 224))
    except Exception as e: 
      # print(e)
      continue
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    # img_array = imagenet_utils.preprocess_input(img_array)
    img_array = preprocess_input(img_array)
    features = cnn_model.predict(img_array)
    # features[0].flatten()
    data.append([features[0].flatten(), price, img_path])
    # x.append([features[0].flatten())
    # y.append(price)
    count += 1
    if count >= NUM_IMAGES: 
      break 
  metadata_file.close()

cnn_end = time.time()
print(f'Time took for generation of feature vectors: {cnn_end - cnn_start} seconds')
print('Size of all data: {}'.format(len(data)))
# data

# save features as csv
features_np = []
for i in range(len(data)):
    features_np.append(np.append(data[i][0], data[i][1]))
    
# skip printing of images to save credits
print(len(data))

# Split trainining and testing data
train_data = []
test_data = []

np.random.shuffle(data)
test_ratio = 0.1
train_data, test_data = np.split(np.array(data,dtype=object), [int(len(data) * (1 - test_ratio))])

print('Size of train data: {}'.format(len(train_data)))
print('Size of test data: {}'.format(len(test_data)))

# Creating two different lists to store the Numpy arrays and the corresponding labels
split_train_start = time.time()
X_train = []                                                                   
y_train = []
train_images = []

for features, label, img_path in train_data:                                           # Iterating over the training data which is generated from the create_training_data() function 
    X_train.append(features)                                                   # Appending images into X_train
    y_train.append(label)     
    train_images.append(img_path)                                                # Appending labels into y_train
# print(y_train)
split_train_end = time.time()
print(f'Time took to split training data: {split_train_end - split_train_start} seconds')

# Creating two different lists to store the Numpy arrays and the corresponding labels
split_test_start = time.time()
X_test = []
y_test = []
test_images = []

for features, label, img_path in test_data:                                            # Iterating over the training data which is generated from the create_testing_data() function
    X_test.append(features)                                                    # Appending images into X_train
    y_test.append(label)  
    test_images.append(img_path)
#print(y_test)  
split_test_end = time.time()
print(f'Time took to split testing data: {split_train_end - split_train_start} seconds')

# Train Linear Regression model
lr_start = time.time()
X_train = np.array(X_train)
lin_reg_model = LinearRegression()
lin_reg_model.fit(X_train, y_train)
lr_end = time.time()
print(f'Time took to train linear regression model: {lr_end - lr_start} seconds')
print(f'Score: {lin_reg_model.score(X_train, y_train)}')

test_start = time.time()
res = lin_reg_model.predict(X_test)
print(f'Score: {lin_reg_model.score(X_test, y_test)}')
test_end = time.time()
print(f'Time took to test linear regression model: {test_end - test_start} seconds')

for i in range(min(len(res), 100)):
    try:
        price = math.exp(res[i])
    except Exception as e:
        print(e)
    print(price, end=" ")
    
def get_stats(pred, out):
    return pd.DataFrame(
        {
            "RMSE": mean_squared_error(out, pred, squared=False),
            "MAE": mean_absolute_error(out, pred),
            "R^2": r2_score(out, pred),
            # "Adjusted R^2": adj_r2(inp, y_act, y_pred),
        },
        index=[0],
    )
    # print(f"RMSE: {mean_squared_error(out, pred, squared=False)}")
    # print(f"MAE: {mean_absolute_error(out, pred)}")
    # print(f"R^2: {r2_score(out, pred)}")

# Checking model performance on train set
print("Training Performance:")
print(get_stats(lin_reg_model.predict(X_train), y_train))

# Checking model performance on test set
print("Test Performance:")
print(get_stats(res, y_test))

def pca_dec(data, n):
    pca = PCA(n)
    X_dec = pca.fit_transform(data)
    return X_dec, pca

for n_dimensions in range(1, 20):
    X_train_reduced, pca_train = pca_dec(X_train, n_dimensions)
    X_test_reduced, pca_test = pca_dec(X_test, n_dimensions)

    X_train_reduced = np.array(X_train_reduced)
    lin_reg_model = LinearRegression()
    lin_reg_model.fit(X_train_reduced, y_train)

    res_reduced = lin_reg_model.predict(X_test_reduced)

    print(f"Number of dimensions: {n_dimensions}")
    print("Training Performance:")
    print(get_stats(lin_reg_model.predict(X_train_reduced), y_train))

    # Checking model performance on test set
    print("Test Performance:")
    print(get_stats(res_reduced, y_test))
    for i in range(min(len(res_reduced), 5)):
        print(math.exp(res_reduced[i]), end=" ")
    print("")
    
for n_dimensions in range(1, 20):
    X_train_reduced, pca_train = pca_dec(X_train, n_dimensions)
    X_test_reduced, pca_test = pca_dec(X_test, n_dimensions)

    X_train_reduced = np.array(X_train_reduced)
    regressor = SVR(kernel='linear')
    regressor.fit(X_train_reduced, y_train)

    res_reduced = regressor.predict(X_test_reduced)

    print(f"Number of dimensions: {n_dimensions}")
    print("Training Performance:")
    print(get_stats(regressor.predict(X_train_reduced), y_train))

    print("Test Performance:")
    print(get_stats(res_reduced, y_test))
    for i in range(min(len(res_reduced), 5)):
        print(math.exp(res_reduced[i]), end=" ")
    print("")
    
regressor = SVR(kernel='sigmoid')
regressor.fit(X_train, y_train)

res_SVR = regressor.predict(X_test)
print(f'Score: {regressor.score(X_test, y_test)}')

clf = SGDRegressor(max_iter=10000, tol=1e-3)
feature_map_nystroem = Nystroem(gamma=.2, random_state=1, n_components=5000)
data_transformed = feature_map_nystroem.fit_transform(X_train)
clf.fit(X_train, y_train)

res = clf.predict(X_test)
print(f'Score: {clf.score(X_test, y_test)}')

sgd_reg = make_pipeline(StandardScaler(), SGDRegressor(max_iter=10000, tol=1e-3))
sgd_reg.fit(X_train, y_train)
res_sgd = sgd_reg.predict(X_test)
print(f'Score: {sgd_reg.score(X_test, y_test)}')

linearSVR_reg = make_pipeline(StandardScaler(), LinearSVR(random_state=0, tol=1e-5))
linearSVR_reg.fit(X_train, y_train)
res_lsvr = linearSVR_reg.predict(X_test)
print(f'Score: {linearSVR_reg.score(X_test, y_test)}')

for i in range(min(len(res_SVR), 100)):
    print(math.exp(res_SVR[i]), end=" ")
print("")

# Checking model performance on train set
print("Training Performance")
print(get_stats(regressor.predict(X_train), y_train))

# Checking model performance on test set
print("Test Performance")
print(get_stats(res_SVR, y_test))

# save the model to disk
filename = 'nft_estimator_model-local.sav'
filepath = f'{rootdir}/outputs/{filename}'
pickle.dump(regressor, open(filepath, 'wb'))
print("============ done! ============")