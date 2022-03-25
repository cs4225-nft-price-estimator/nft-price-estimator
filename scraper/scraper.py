import cloudscraper
import json
import os 
import scraper_utils
from scraper_source import slugs

dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox', # use chrome if this doesnt work
        'platform': 'android',
        'desktop': True 
    }
)

def get_floor_prices(slug):
  url = "https://opensea.io/collection/{}?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW".format(slug);
  html = scraper.get(url).text
  json_string = html.split("</script>",2)[0].split("window.__wired__=",2)
  json_string = json_string[1] if len(json_string) == 2 else ""
  data = json.loads(json_string)
  data_values = data["records"].values() # get all values type...
  data_list = [*data_values]
  # get metadata of images
  images = list(filter(scraper_utils.filter_images, data_list))
  images = list(map(scraper_utils.filter_metadata, images))
  images = list(filter(lambda x: x is not None, images))
  # get prices of images
  data_list = list(filter(scraper_utils.filter_typename, data_list))
  prices_data_list = list(filter(scraper_utils.filter_quantityInEth_exists, data_list))
  prices_data_list = list(map(scraper_utils.get_floor_price_in_eth, prices_data_list))
  prices_data_list = sorted(prices_data_list)
  # format results
  result = list(zip(prices_data_list, images))
  result = list(map(scraper_utils.format_result, result))
  return result

# Structure (priceInEth: float, { id: int, name: str, image: str })
def scrape_slug(slug: str):
  print("================ Running for {} ================".format(slug))
  try:
    data = get_floor_prices(slug)
    print("Total {} NFTS scraped".format(len(data)))
    scraper_utils.write_json_to_file('{}/scraped-collections/{}.json'.format(dir_path, slug), data)
    for obj in data:
      print(obj)
  except Exception as e:
    print("@@@@@@@@@@@@@@ ERROR ERROR ERROR @@@@@@@@@@@@@@@ ")
    print(e)
    print("FAILURE: Unable to scrape for {} collection".format(slug))
  print("=================== Ended ========================")

def scrape_all():
  test = input('Scrape all? (Y/N)')
  if test == 'Y' or test == 'y' or test == 'yes':
    for collection in slugs:
      scrape_slug(collection)
    
# TEST
def main():
  # scrape_slug(slugs[2])
  scrape_all()

if __name__ == "__main__":
    main()


