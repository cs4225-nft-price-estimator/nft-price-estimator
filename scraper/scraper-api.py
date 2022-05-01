import json
import requests
import urllib.request as req
import os
import multiprocessing
from crypto_collections import final_collections
from scraper_utils import write_json_to_file
from scraper_utils import get
from scraper_source import slugs

api = 'https://api.opensea.io/api/v1'
API_KEY = 'API_KEY' # update with your own API_KEY
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
        'image': asset['image_url'],
        'price': float(float(asset['last_sale']['total_price'])/1000000000000000000),
        'token': asset['last_sale']['payment_token']['symbol']
    }

def getMetadataOfCurrentSet(dict):
    transacted_assets = list(filter(haveSoldBeforeFilter, dict))
    return list(map(getMetadata, transacted_assets))

def getCollectionContractAddress(slug):
    assets_endpoint = api + '/collection/{}'.format(slug)
    response = requests.get(assets_endpoint)
    response = json.loads(response.text)
    try:
        return response['collection']['primary_asset_contracts'][0]['address']
    except:
        return None

def getAsset(contract_address, c_limit=None):
    limit = 50
    assets_endpoint = api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&include_orders=false'.format(contract_address, limit)
    LAMBDA_ASSET_ENDPOINT_WITH_CURSOR = lambda cursorX: api + '/assets?order_direction=desc&asset_contract_address={}&limit={}&cursor={}&include_orders=false'.format(contract_address, limit, cursorX)
    headers = {
        "Accept": "application/json",
        "X-API-KEY": API_KEY
    }
    response = get(assets_endpoint, headers=headers, session=None)
    data: list = response['assets']
    data = getMetadataOfCurrentSet(data)
    cursor = response['next']
    c = 0
    c_limit = 20
    with requests.Session() as session:
        try:
            while (cursor):
                if c_limit is not None and c >= c_limit:
                    break
                encoded_cursor = req.pathname2url(cursor)
                assets_endpoint_cursor = LAMBDA_ASSET_ENDPOINT_WITH_CURSOR(encoded_cursor)
                response = get(assets_endpoint_cursor, headers, session)
                
                if not(response): # handle cases where requests is too slow in getting the data
                    c += 1
                    continue
                cursor, curr = response['next'], response['assets']
                if cursor: # if we have not reached the end of collection
                    print('Iteration {}: '.format(c) + cursor)
                    data.extend(getMetadataOfCurrentSet(curr))
                    c += 1
                else:
                    break
        except Exception as err:
            print("ERROR getAsset() for {}: ".format(contract_address) + str(err))

    return data

dir_path = os.path.dirname(os.path.realpath(__file__)) # get current directory

def scrape_collection_api(slug: str, c_limit=None): 
    print("-------- Test for test_slug = {} --------".format(slug))     
    addr = getCollectionContractAddress(slug)
    print("Address ={}".format(addr))
    if addr is not None:
        data = getAsset(addr, c_limit)
        write_json_to_file("{dir}/scraped_api_collections/{slug}.json".format(dir=dir_path, slug=slug), data)
        print(len(data), "NFTs scraped for \'{}\'".format(slug))
        hashSet.clear()
    else:
        print("Address is not availabled for \'{}\'".format(slug))

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

def parallelized_scrape():
    with multiprocessing.Pool(5) as p:
        p.map(scrape_collection_api, final_collections);
    # pool = multiprocessing.Pool()
    # pool.map(scrape_collection_api, final_collections)
    ### To note
    # chunksize = 5 # for a long set of iterables, assign 5 items as a task to a processor
    # pool.imap(scrape_collection_api, final_collections, chunksize=chunksize)
def main():
    # Test eg. slug = cryptopunks
    # test_slug = 'cryptopunks'
    # print("-------- Test for test_slug = {} --------".format(test_slug))
    # for col in final_collections:
    #     scrape_collection_api(col)
    # Scrape all API
    scrape_all_slugs_api()

rescrape = [
    # 'the-picaroons',
    # 'mirlclub',
    'frenlypandas',
]
if __name__ == "__main__":
    for col in rescrape:
        scrape_collection_api(col)
    
    # parallelized_scrape() #dangerous command
    # main()