## For database search tool
from typing import TypedDict, Optional, NotRequired, Literal
from langchain_openai import OpenAIEmbeddings
from crm.utils import load_project_db
import os


class CustomerInformationInput(TypedDict):
    name: NotRequired[str]
    age: NotRequired[Literal["<16", "16-25", "25-40", "40-55", ">55"]]
    gender: NotRequired[str]
    special_occasions: NotRequired[str]
    price_sensitivity: NotRequired[str]
    hobbies_interests: NotRequired[str]
    preferred_products_categories: NotRequired[str]
    preferred_brands: NotRequired[str]


def save_customer_information(input_dict:CustomerInformationInput):
    """ this function to save customers persona data and interests into the databases.
        when no field required, do not pass parameter string of "None" or "Unknown".
    """
    # get database
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    CURRENT_USER_ID = os.environ["CURRENT_USER_ID"]
    
    st = ""
    for k,v in input_dict.items():
        st += f"{k}: {v}\n"
    
    embedding = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=20)
    embeded = embedding.embed_query(st)
    
    input_dict['embedding'] = embeded
        
    # Update the document in MongoDB
    costomer_collection.update_one(
        {"user_id": CURRENT_USER_ID},
        {"$set": 
            input_dict
        },
        upsert=True  # Create a new document if no matching document is found
    )
    
    client.close()
    
    return get_customer_information_by_id(user_id=CURRENT_USER_ID)


def update_embedding(user_id:str, exclude_fields:list[str]=['_id', 'active_time', 'user_id'], model="text-embedding-3-small", dimensions=20):
    """ this function to save customers persona data and interests into the databases.
    """
    # get database
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    info_dict = get_customer_information_by_id(user_id=user_id)
    
    st = ""
    for k,v in info_dict.items():
        if k not in exclude_fields:
            st += f"{k}: {v}\n"
    
    embedding = OpenAIEmbeddings(model=model, dimensions=dimensions)
    embeded = embedding.embed_query(st)
    
    info_dict['embedding'] = embeded
        
    # Update the document in MongoDB
    costomer_collection.update_one(
        {"user_id": user_id},
        {"$set": 
            info_dict
        }
    )
    
    client.close()
    
    return info_dict


def get_customer_information_by_id(user_id:str):
    """ this function to get customers persona data and interests into the databases.
    """
    # get database
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    # Update the document in MongoDB
    persona = costomer_collection.find_one(
        {"user_id": user_id.strip()}
    )
    
    client.close()
    
    if persona:
        return dict(persona)
    else:
        return 'No data'
    

def get_all():
    client, db = load_project_db()
    costomer_collection = db["Customer"]
    
    result = list(costomer_collection.find())
    
    client.close()
    return result
    
## deprecated
# def get_customer_information():
#     """ this function to get customers persona data and interests into the databases.
#     """
#     # get database
#     client, db = load_project_db()
#     costomer_collection = db["Customer"]
    
#     CURRENT_USER_ID = os.environ["CURRENT_USER_ID"]
    
#     # Update the document in MongoDB
#     persona = costomer_collection.find_one(
#         {"user_id": CURRENT_USER_ID}
#     )
    
#     client.close()
    
#     if persona:
#         return dict(persona)
#     else:
#         return 'No data'
