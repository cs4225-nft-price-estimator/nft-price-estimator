import json
import requests
import urllib.request as req

api = 'https://api.opensea.io/api/v1'
API_KEY = '2f6f419a083c46de9d83ce3dbe7db601'
test_address = '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb'
url = "https://api.opensea.io/api/v1/assets?order_direction=desc&asset_contract_address=0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb&limit=20&cursor=LXBrPTUzMTA1Mg%3D%3D&include_orders=false"

def haveSoldBeforeFilter(asset):
    return asset['last_sale'] and asset['last_sale']['total_price'] and float(asset['last_sale']['total_price']) > 0

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
    response = requests.request("GET", assets_endpoint)
    response = json.loads(response.text)
    return response['collection']['primary_asset_contracts'][0]['address']

def getAsset(contract_address):
    limit = 20
    assets_endpoint = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&include_orders=false'.format(contract_address, limit)
    assets_endpoint_cursor = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&cursor={}&include_orders=false' # cursor needs to be URL encoded
    headers = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY
    }
    response = requests.request("GET", assets_endpoint, headers=headers)
    response = json.loads(response.text)
    data: list = response['assets']
    transacted_assets = list(filter(haveSoldBeforeFilter, data))
    data = list(map(getMetadata, transacted_assets))
    cursor = response['next']
    c = 0
    while (cursor and c < 4):
        encoded_cursor = req.pathname2url(cursor)
        assets_endpoint_cursor = assets_endpoint_cursor.format(contract_address, limit, encoded_cursor)
        response = requests.request("GET", assets_endpoint_cursor, headers=headers)
        response = json.loads(response.text)
        cursor = response['next']
        print(cursor) # Issue: Async call not awaited hence same items are fetched
        curr = response['assets']
        transacted_assets = list(filter(haveSoldBeforeFilter, curr))
        data = data + list(map(getMetadata, transacted_assets))
        c += 1
    return data

        
addr = getCollectionContractAddress('cryptopunks')
print(getAsset(test_address))
