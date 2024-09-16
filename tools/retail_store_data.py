## For database search tool
from langchain_openai import OpenAIEmbeddings
import pymongo.collection
import numpy as np
from numpy.linalg import norm
from utils import load_project_db
import os

STORE_NAME = os.environ["STORE_NAME"]

#! Retriever
embedding = OpenAIEmbeddings(model="text-embedding-3-small")


def similarity_search(collection:pymongo.collection.Collection, query:str, embedding:OpenAIEmbeddings, k:int=4, include_score:bool=False):
    items = list(collection.find({"name": STORE_NAME}))
    for item in items:
        emb = item['embedding']

        a = emb
        b = embedding.embed_query(query)

        cosine = np.dot(a,b)/(norm(a)*norm(b))
        
        item['score']=cosine

    sorted_items = sorted(items, reverse=True, key=lambda d: d['score'])

    sorted_items = sorted_items[:k]
    
    for item in sorted_items:
        del item['embedding']
        if not include_score: del item['score'] 

    return sorted_items


def search_retail_store(query:str):
    """ search in retail store database.
    """
    # get database
    client, db = load_project_db()
    products_collection = db["Products"]
    stores_collection = db["Stores"]
    
    items = similarity_search(stores_collection ,query, embedding=embedding, k=1)
    for item in items:
        for product in item['products']:
            detail = list(products_collection.find({"_id": product['id']}))[0]
            del detail['embedding']
            product = product.update( detail )
            
    client.close()
    return str(items)
    

# def search_product_data(query:str):
#     """ search in product database.
#     """
#     items = similarity_search(products_collection ,query, embedding=embedding, k=1)
#     for item in items:
#         del item['embedding']
#         del item['score']
#     return str(items)