import json
import requests
import urllib.request as req
import os
from scraper_utils import write_json_to_file

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
    # if asset['last_sale'] and asset['last_sale']['total_price'] and float(asset['last_sale']['total_price']) > 0:
    return {
        'id': int(asset['token_id']),
        'name': asset['name'],
        'image': asset['collection']['image_url'],
        'price': float(float(asset['last_sale']['total_price'])/1000000000000000000)
    }

def getCollectionContractAddress(slug):
    assets_endpoint = api + '/collection/{}'.format(slug)
    response = requests.get(assets_endpoint)
    response = json.loads(response.text)
    return response['collection']['primary_asset_contracts'][0]['address']

def getAsset(contract_address):
    # limit = 20
    limit = 50
    assets_endpoint = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&include_orders=false'.format(contract_address, limit)
    # assets_endpoint_cursor = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&cursor={}&include_orders=false' # cursor needs to be URL encoded
    LAMBDA_ASSET_ENDPOINT_WITH_CURSOR = lambda cursorX: api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&cursor={}&include_orders=false'.format(contract_address, limit, cursorX)
    headers = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY
    }  
    response = requests.get(assets_endpoint, headers=headers)
    response = json.loads(response.text)
    data: list = response['assets']
    transacted_assets = list(filter(haveSoldBeforeFilter, data))
    data = list(map(getMetadata, transacted_assets))
    cursor = response['next']
    c = 0
    c_limit = 20
    while (cursor and c < c_limit):
        encoded_cursor = req.pathname2url(cursor)
        assets_endpoint_cursor = LAMBDA_ASSET_ENDPOINT_WITH_CURSOR(encoded_cursor)
        response = requests.request("GET", assets_endpoint_cursor, headers=headers)
        response = json.loads(response.text)
        cursor = response['next']
        print(cursor) # Issue: Async call not awaited hence same items are fetched
        curr = response['assets']
        transacted_assets = list(filter(haveSoldBeforeFilter, curr))
        data = data + list(map(getMetadata, transacted_assets))
        c += 1
    return data

dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory

def scrape_collection_api(slug: str):      
    addr = getCollectionContractAddress(slug)
    print("Address ={}".format(addr))
    data = getAsset(addr)
    write_json_to_file("{dir}/collections/{slug}.json".format(dir=dir_path, slug=slug), data)
    print(len(data), "NFTs scraped")

scrape_collection_api('cryptopunks')
