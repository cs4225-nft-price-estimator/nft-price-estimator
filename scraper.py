import cloudscraper
import json

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox', # use chrome if this doesnt work
        'platform': 'android',
        'desktop': True 
    }
)

def filter_typename(dict):
  return dict["__typename"] == "AssetQuantityType"

def filter_images(dict):
  return dict["__typename"] == "AssetType"

def filter_metadata(dict):
  if "tokenId" in dict:
    return {
      'id': dict["tokenId"],
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

def get_floor_prices(slug):
  url = "https://opensea.io/collection/{}?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW".format(slug);
  html = scraper.get(url).text
  json_string = html.split("</script>",2)[0].split("window.__wired__=",2)
  json_string = json_string[1] if len(json_string) == 2 else ""
  data = json.loads(json_string)
  data_values = data["records"].values() # get all values type...
  data_list = [*data_values]
  # get metadata of images
  images = list(filter(filter_images, data_list))
  images = list(map(filter_metadata, images))
  # get prices of images
  data_list = list(filter(filter_typename, data_list))
  prices_data_list = list(filter(filter_quantityInEth_exists, data_list))
  prices_data_list = list(map(get_floor_price_in_eth, data_list))
  return prices_data_list, images

def write_data_to_file(filename, data):
  with open(filename, 'w') as f:
    json.dump(json.dumps(data, ensure_ascii=False, indent=4), f)
  f.close()

def write_json_to_file(filename, json_string):
  with open(filename, 'w') as f:
    f.write(json_string)
  f.close()

# scraping floor prices from opensea
# print("RUNNING FOR cool-cats-nft")
# print(get_floor_prices("cool-cats-nft"))

print("RUNNING FOR mirlclub")
data = get_floor_prices("mirlclub")
print(data)

# url='https://opensea.io/collection/cool-cats-nft?tab=activity'
# try to scrape activity tab for transaction details