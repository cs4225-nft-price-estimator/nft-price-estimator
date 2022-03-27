import json
import requests

api = 'https://api.opensea.io/api/v1'
API_KEY = '2f6f419a083c46de9d83ce3dbe7db601'
test_address = '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb'
url = "https://api.opensea.io/api/v1/assets?order_direction=desc&asset_contract_address=0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb&limit=20&cursor=LXBrPTUzMTA1Mg%3D%3D&include_orders=false"

def getMetadata(asset):
    if asset['last_sale'] and asset['last_sale']['total_price'] and float(asset['last_sale']['total_price']) > 0:
        return {
            'id': int(asset['token_id']),
            'name': asset['name'],
            'image': asset['collection']['image_url'],
            'price': float(float(asset['last_sale']['total_price'])/1000000000000000000)
        }

def getAsset(contract_address):
    limit = 20
    assets_endpoint = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&include_orders=false'.format(contract_address, limit)
    assets_endpoint_cursor = api + 'assets?order_direction=desc&asset_contract_address={}&limit=50&cursor={}&include_orders=false' # cursor needs to be URL encoded
    headers = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY
    }
    response = requests.request("GET", assets_endpoint, headers=headers)
    response = json.loads(response.text)
    data = response['assets']
    return list(map(getMetadata, data))


print(getAsset(test_address))