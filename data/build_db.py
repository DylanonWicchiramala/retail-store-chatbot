# append project work dir path
from os.path import dirname, realpath, sep, pardir
import sys
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

import json
import os
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import pymongo
from utils import load_env

load_env()

# Load MongoDB credentials and set up the connection
mongo = os.environ.get('MONGODB_PASS')
uri = f"mongodb+srv://dylan:{mongo}@cluster0.wl8mbpy.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

# Connect to the "RetailStore" database
db = client["RetailStore"]

# Define the collections
stores_collection = db["Stores"]
products_collection = db["Products"]


def create_collection_from_json(path: str, collection: pymongo.collection.Collection):
    # Load data from the provided JSON file
    with open(path) as file:
        data = json.load(file)

    # Upsert (insert or replace) each document in the collection
    for record in data:
        # Ensure each record has an `_id` field to use for upsert
        filter_criteria = {"_id": record["_id"]}
        collection.replace_one(filter_criteria, record, upsert=True)
    
    print(f"Upserted {len(data)} records into the collection.")


create_collection_from_json(path="data/product.json", collection=products_collection)
create_collection_from_json(path="data/store.json", collection=stores_collection)


# Close the MongoDB connection
client.close()