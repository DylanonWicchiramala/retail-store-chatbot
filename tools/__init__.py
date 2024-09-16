# %%
## Document vector store for context
from langchain_core.tools import tool
import functools
from copy import copy
## For database search tool
from langchain_openai import OpenAIEmbeddings
import pymongo.collection
import numpy as np
from numpy.linalg import norm
from utils import load_project_db
import os

STORE_NAME = os.environ["STORE_NAME"]

client, db = load_project_db()

#! Retriever
embedding = OpenAIEmbeddings(model="text-embedding-3-small")
#? Vector store
products_collection = db["Products"]
stores_collection = db["Stores"]


tools_outputs=""


def get_tools_output():
    global tools_outputs
    result = copy(tools_outputs)
    tools_outputs = ""
    return result


def save_tools_output(func):
    @functools.wraps(func) 
    def wrapper(*args, **kwargs):
        global tools_outputs
        # Call the original function and get its return value
        result = func(*args, **kwargs)
        # Append the result to tools_outputs
        tools_outputs += str(result) + "\n"
        # Return the original result
        return result
    return wrapper


def similarity_search(collection:pymongo.collection.Collection, query:str, embedding:OpenAIEmbeddings, k:int=4, threshold:float=0.55, include_score:bool=False):
    items = list(collection.find({"name": STORE_NAME}))
    for item in items:
        emb = item['embedding']

        a = emb
        b = embedding.embed_query(query)

        cosine = np.dot(a,b)/(norm(a)*norm(b))
        
        item['score']=cosine

    filtered_items = filter(lambda d: d['score']>=threshold, items)
    
    sorted_items = sorted(filtered_items, reverse=True, key=lambda d: d['score'])

    sorted_items = sorted_items[:k]
    
    for item in sorted_items:
        del item['embedding']
        if not include_score: del item['score'] 

    return sorted_items

# %%
@tool
# @save_tools_output
def search_retail_store(query:str):
    """ search in retail store database.
    """
    items = similarity_search(stores_collection ,query, embedding=embedding, k=1)
    for item in items:
        for product in item['products']:
            detail = list(products_collection.find({"_id": product['id']}))[0]
            del detail['embedding']
            product = product.update( detail )
    return str(items)
    

# @tool
# @save_tools_output
# def search_product_data(query:str):
#     """ search in product database.
#     """
#     items = similarity_search(products_collection ,query, embedding=embedding, k=1)
#     for item in items:
#         del item['embedding']
#         del item['score']
#     return str(items)


all_tools = [search_retail_store]