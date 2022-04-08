import json
import math
from os import getenv

from algoliasearch.search_client import SearchClient
from algoliasearch.exceptions import RequestException
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
# Algolia client credentials
ALGOLIA_APP_ID = getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX_NAME = getenv('ALGOLIA_INDEX')

print(f'Starting Algolia client...')
client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
index = client.init_index(ALGOLIA_INDEX_NAME)
index.delete().wait()

index_data_path = './data/products.json'
product_category = 'Cameras & Camcorders'
price_reduction_percent = 20

def load_json_data(data_path):
    '''Load a JSON data file and returns a JSON dict object.
    '''
    with open(data_path, 'r', encoding = 'utf-8') as json_file:
        data = json.load(json_file)
    return data


def reduce_price_by_category(data, category_name, percentage):
    '''Reduce the price field value by the percentage provided in all products in category_name.
    '''
    for product in data:
        if category_name in product['categories']:
            product['price'] = math.floor(round((product['price'] * (1 - percentage/100)), 2))


def index_data(data):
    '''Send data to Algolia for indexing.'''
    try:
        index.save_objects(data,{}).wait()
    except RequestException as e:
        print(e.args[0])


print(f'Loading Data from {index_data_path}')
products_data = load_json_data(index_data_path)
print(f'Reducing prices by {price_reduction_percent}% in {product_category} category')
reduce_price_by_category(products_data, product_category, price_reduction_percent)

print(f'Configure Index Settings')
index.set_settings({
  'searchableAttributes': [
    'name',
    'description'
  ],
  'customRanking': [
    'desc(popularity)',
    'desc(rating)',
  ],
  'attributesForFaceting': [
    'brand',
    'categories',
    'price_range',
    'rating',
  ],
    "renderingContent": {
      "facetOrdering": {
        "facets": {
          "order": [
            "rating",
            "price_range"
          ]
        },
        "values": {
          "price_range": {
            "order": [
              "1 - 50",
              "50 - 100",
              "100 - 200",
              "200 - 500",
              "500 - 2000",
              "> 2000"
            ],
            "sortRemainingBy": "hidden"
          },
          "rating": {
            "order": [
              "6",
              "5",
              "4",
              "3",
              "2",
              "1"
            ],
            "sortRemainingBy": "hidden"
          }
        }
      }
    }
})

print(f'Add Records to Index')
index_data(products_data)