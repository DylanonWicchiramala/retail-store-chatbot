## For database search tool
from langchain_openai import OpenAIEmbeddings
from crm.tools.mongodb_search import similarity_search
from crm.utils import load_project_db

#! Retriever
embedding = OpenAIEmbeddings(model="text-embedding-3-small")

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