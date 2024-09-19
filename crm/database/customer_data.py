## For database search tool
from typing import TypedDict, Optional, NotRequired, Literal
from crm.utils import load_project_db
import os


class CustomerInformationInput(TypedDict):
    name: NotRequired[str]
    age: NotRequired[int]
    gender: NotRequired[str]
    special_occasions: NotRequired[str]
    price_sensitivity: NotRequired[str]
    hobbies_interests: NotRequired[str]
    preferred_products_categories: NotRequired[str]
    preferred_brands: NotRequired[str]


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
    
    return get_customer_information_by_id(user_id=CURRENT_USER_ID)
    
## deprecated
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
        return 'No data'


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