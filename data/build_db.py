# append project work dir path
from os.path import dirname, realpath, sep, pardir
import sys
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

import json
import pymongo
from utils import load_retail_store_db
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

client, db = load_retail_store_db()

# Define the collections
stores_collection = db["Stores"]
products_collection = db["Products"]

embedding = OpenAIEmbeddings(model="text-embedding-3-small")


# Function to concatenate all text fields into one string
def concatenate_fields(document, fields=None):
    fields = fields if fields else list(document.keys())
    return "\n".join([ f"{document.get(field, 'None')}" for field in fields])


# Function to generate embeddings and update the MongoDB collection
def populate_embeddings(collection, fields, embedding_key="embedding"):
    documents = collection.find()
    
    for doc in documents:
        # Concatenate all relevant fields
        combined_text = concatenate_fields(doc, fields)
        
        # Generate the embedding for the combined text
        embeded = embedding.embed_query(combined_text)

        # Update the document with the generated embedding
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {embedding_key: embeded}}
        )
        print(f"Updated store {doc['_id']} with embedding.")
        
    return collection


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
    
    return collection


if __name__=="__main__":
    products_collection.delete_many({})
    stores_collection.delete_many({})

    products_collection = create_collection_from_json(path="data/product.json", collection=products_collection)
    stores_collection = create_collection_from_json(path="data/store.json", collection=stores_collection)

    products_collection = populate_embeddings(products_collection, fields=None)
    stores_collection = populate_embeddings(stores_collection, fields=None)


# Close the MongoDB connection
client.close()