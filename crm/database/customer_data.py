## For database search tool
from typing import TypedDict, Optional, NotRequired, Literal
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from crm.utils import load_project_db
import os


class CustomerInformationInput(TypedDict):
    name: NotRequired[str]
    age: NotRequired[Literal["<16", "16-25", "25-40", "40-55", ">55"]]
    gender: NotRequired[str]
    special_occasions: NotRequired[str]
    price_sensitivity: NotRequired[Literal["sensitive", "medium", "non-sensitive"]]
    hobbies_interests: NotRequired[str]
    needs_wants: NotRequired[str]
    preferred_products_categories: NotRequired[str]
    preferred_brands: NotRequired[str]
    marital_status: NotRequired[Literal["marriage", "never married", "divorced", "widowed", "separated"]]


def save_customer_information(user_id: str, input_dict: CustomerInformationInput):
    """This function saves customer persona data and interests into the database.
       When no field is required, do not pass a parameter with a string of "None" or "Unknown".
    """
    # Get database
    client, db = load_project_db()
    customer_collection = db["Customer"]

    # Convert customer data input_dict to string for embedding.
    st = ""
    for k, v in input_dict.items():
        st += f"{k}: {v}\n"

    embedding = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=20)
    embedded = embedding.embed_query(st)

    # Add embedding and current datetime
    input_dict['embedding'] = embedded
    input_dict['latest_update'] = datetime.now()  # Add the current datetime

    # Update the document in MongoDB
    customer_collection.update_one(
        {"user_id": user_id},
        {"$set": input_dict},
        upsert=True  # Create a new document if no matching document is found
    )

    client.close()

    return get_customer_information_by_id(user_id=user_id)


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


def get_all_user_ids():
    user_data = get_all()
    
    user_ids = []
    for item in user_data:
        user_ids.append(item['user_id'])
    
    return user_ids

    
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
