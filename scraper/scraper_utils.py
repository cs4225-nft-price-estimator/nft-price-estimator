import json


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

def write_data_to_file(filename, data):
  with open(filename, 'w+') as f:
    json.dump(json.dumps(data, ensure_ascii=False, indent=4), f)
  f.close()

def write_json_to_file(filename, json_string):
  with open(filename, 'w+') as f:
    json.dump(json_string, f, indent=4)
  f.close()