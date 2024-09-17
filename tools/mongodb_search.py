from langchain_openai import OpenAIEmbeddings
import pymongo.collection
import numpy as np
from numpy.linalg import norm
import os

STORE_NAME = os.environ["STORE_NAME"]

def similarity_search(collection:pymongo.collection.Collection, query:str, embedding:OpenAIEmbeddings, k:int=4, threshold:float=0.10, include_score:bool=False):
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