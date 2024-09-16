## For database search tool
from typing import TypedDict, Optional, NotRequired, Literal
from langchain_openai import OpenAIEmbeddings
import pymongo.collection
import numpy as np
from numpy.linalg import norm
from utils import load_project_db
import os

STORE_NAME = os.environ["STORE_NAME"]

#! Retriever
embedding = OpenAIEmbeddings(model="text-embedding-3-small")


class CustomerInformationInput(TypedDict):
    name: NotRequired[str]
    age: NotRequired[int]
    gender: NotRequired[str]
    special_occasions: NotRequired[str]
    price_sensitivity: NotRequired[str]
    hobbies_interests: NotRequired[str]
    preferred_products_categories: NotRequired[str]
    preferred_brands: NotRequired[str]


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


def save_customer_information(input_dict:CustomerInformationInput):
    """ this function to save customers persona data and interests into the databases.
    """
    # get database
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    CURRENT_USER_ID = os.environ["CURRENT_USER_ID"]
    
    # Update the document in MongoDB
    costomer_collection.update_one(
        {"user_id": CURRENT_USER_ID},
        {"$set": 
            input_dict
        },
        upsert=True  # Create a new document if no matching document is found
    )
    
    client.close()
    
    return get_customer_information()
    

def get_customer_information():
    """ this function to get customers persona data and interests into the databases.
    """
    # get database
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    CURRENT_USER_ID = os.environ["CURRENT_USER_ID"]
    
    # Update the document in MongoDB
    persona = costomer_collection.find_one(
        {"user_id": CURRENT_USER_ID}
    )
    
    client.close()
    
    if persona:
        return dict(persona)
    else:
        return None