import json
import requests
from requests.sessions import Session
import os

def filter_typename(dict):
  return dict["__typename"] == "AssetQuantityType"

def filter_images(dict):
  return dict["__typename"] == "AssetType"

def filter_metadata(dict):
  if "tokenId" in dict:
    return {
      'id': int(dict["tokenId"]),
      'name': dict["name"],
      'image': dict["displayImageUrl"]
    }
  else:
    return

def filter_quantityInEth_exists(dict):
  if "quantityInEth" in dict:
    return True
  else:
    return False

def get_floor_price_in_eth(dict):
  return float(dict["quantity"]) / 1000000000000000000

def format_result(pair):
  return {
    "price": pair[0],
    "id": pair[1]["id"],
    "name": pair[1]["name"],
    "image": pair[1]["image"]
  }

def get(endpoint, headers, session:Session):
  if not(session):
    response = requests.get(endpoint, headers=headers)
    return json.loads(response.text)
  else:  
    with session.get(endpoint, headers=headers) as response:
      return json.loads(response.text)

def write_data_to_file(filename, data):
  with open(filename, 'w+') as f:
    json.dump(json.dumps(data, ensure_ascii=False, indent=4), f)
  f.close()

def write_json_to_file(filename, json_arr):
  os.makedirs(os.path.dirname(filename), exist_ok=True) # Create the relevant directory & file not present
  with open(filename, 'w+') as f:
    for i in json_arr:
      json.dump(i, f)
      f.write("\n")
  f.close()
  
def download_image(folder: str, filename: str, image_url: str):
  if not os.path.exists(folder):
    os.makedirs(folder)
  with open(folder + '/' + filename, 'wb') as f:
    f.write(requests.get(image_url).content)
    f.close()
   
# dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory
# scraper_utils.download_image('{}/assets/cool-cats-nft'.format(dir_path), '4807.png', 'https://lh3.googleusercontent.com/VwXwtH0-4-Np1DrsK5X1u102Je_Ju2FUH8yltByPOEKONeEDBNcs6poEjElhKWeAKquhzpdQwqS_hJGV-O-a3iy7GgPjYVLduxAWKdg')
