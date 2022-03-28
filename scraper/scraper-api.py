import json
import requests
import urllib.request as req
import os
from scraper_utils import write_json_to_file
from scraper_utils import get
from scraper_source import slugs

api = 'https://api.opensea.io/api/v1'
API_KEY = '2f6f419a083c46de9d83ce3dbe7db601'
test_address = '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb'
url = "https://api.opensea.io/api/v1/assets?order_direction=desc&asset_contract_address={test_address}&limit=20&cursor=LXBrPTUzMTA1Mg%3D%3D&include_orders=false".format(test_address=test_address)

hashSet = set()
def haveSoldBeforeFilter(asset):
    asset_id = int(asset['token_id'])
    if asset_id not in hashSet:
        hashSet.add(asset_id)
        return asset['last_sale'] and asset['last_sale']['total_price'] and float(asset['last_sale']['total_price']) > 0
    return False

def getMetadata(asset):
    return {
        'id': int(asset['token_id']),
        'name': asset['name'],
        'image': asset['collection']['image_url'],
        'price': float(float(asset['last_sale']['total_price'])/1000000000000000000)
    }

def getMetadataOfCurrentSet(dict):
    transacted_assets = list(filter(haveSoldBeforeFilter, dict))
    return list(map(getMetadata, transacted_assets))

def getCollectionContractAddress(slug):
    assets_endpoint = api + '/collection/{}'.format(slug)
    response = requests.get(assets_endpoint)
    response = json.loads(response.text)
    return response['collection']['primary_asset_contracts'][0]['address']

def getAsset(contract_address, c_limit=None):
    limit = 50
    assets_endpoint = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&include_orders=false'.format(contract_address, limit)
    LAMBDA_ASSET_ENDPOINT_WITH_CURSOR = lambda cursorX: api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&cursor={}&include_orders=false'.format(contract_address, limit, cursorX)
    headers = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY
    }  
    response = get(assets_endpoint, headers)
    data: list = response['assets']
    data = getMetadataOfCurrentSet(data)
    cursor = response['next']
    c = 0
    c_limit = 20
    with requests.Session() as session:
        while (cursor):
            if c_limit is not None and c >= c_limit:
                break
            encoded_cursor = req.pathname2url(cursor)
            assets_endpoint_cursor = LAMBDA_ASSET_ENDPOINT_WITH_CURSOR(encoded_cursor)
            response = get(assets_endpoint_cursor, headers, session)
            cursor, curr = response['next'], response['assets']
            if cursor:
                print('Iteration {}: '.format(c) + cursor)
            data.extend(getMetadataOfCurrentSet(curr))
            c += 1
    return data

dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory

def scrape_collection_api(slug: str, c_limit=None):      
    addr = getCollectionContractAddress(slug)
    print("Address ={}".format(addr))
    data = getAsset(addr, c_limit)
    write_json_to_file("{dir}/scraped_api_collections/{slug}.json".format(dir=dir_path, slug=slug), data)
    print(len(data), "NFTs scraped")
    hashSet.clear()

def scrape_all_slugs_api():
    scrape_all = input("Scrape all collections using OpenSea API? (Y/N) ")
    if scrape_all == 'Y' or scrape_all == 'y' or scrape_all == 'yes':
        try:
            c_limit = int(input("Enter limit per api call: "))
            for slug in slugs:
                scrape_collection_api(slug, c_limit)
        except:
            for slug in slugs:
                scrape_collection_api(slug)
    else:
        scrape_one = input("Scrape one collection using OpenSea API? (Y/N) ")
        if scrape_one == 'Y' or scrape_one == 'y' or scrape_one == 'yes':
            slug = input("Enter slug: ")
            scrape_collection_api(slug)

def main():
    # Test eg. slug = cryptopunks
    test_slug = 'cryptopunks'
    print("-------- Test for test_slug = {} --------".format(test_slug))
    scrape_collection_api(test_slug)
    # Scrape all API
    scrape_all_slugs_api()

if __name__ == "__main__":
    main()