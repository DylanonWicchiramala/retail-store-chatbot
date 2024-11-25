from typing import TypedDict
from bson import ObjectId
import utils
import database
from database import chat_history
from utils import bundle_input
from line_bot import __use_line_api
import re

utils.load_env()

COLLECTION_NAME = "User Profile"

class UserProfileSchema(TypedDict):
    user_id: str
    display_name: str
    picture_url: str
    status_message: str
    language: str
    

class QuerySchema(UserProfileSchema):
    _id:str
    upsert:bool


def add(data: UserProfileSchema) -> dict:
    # connect db
    client, db = database.load_db()
    collection = db[COLLECTION_NAME]
    
    # Insert the order into the collection
    inserted_id = collection.insert_one(data).inserted_id
    
    # Retrieve the newly inserted document
    result = collection.find_one({"_id": inserted_id})
    
    client.close()
    return result


def update(query:QuerySchema, data: UserProfileSchema) -> dict:
    # connect db
    client, db = database.load_db()
    collection = db[COLLECTION_NAME]
    
    upsert = query.pop("upsert", True)
    
    # Retrieve the newly inserted document
    collection.update_one(
        query,
        {"$set": data},
        upsert = upsert
    )
    
    client.close()
    return get(query)


def get(query:QuerySchema, *query_args, **query_kwargs) -> list[dict]:
    client, db = database.load_db()
    collection = db[COLLECTION_NAME]
    
    result = list(collection.find(query, *query_args, **query_kwargs))
    
    client.close()
    return result


def delete(query:QuerySchema=None) -> list[dict]:
    client, db = database.load_db()
    collection = db[COLLECTION_NAME]
    
    res = collection.delete_many(query)  # Delete documents matching the query
    client.close()
    return res


def update_pipeline(user_id=None):
    """ if user_id is None, get users profile from chat_history database.
    """
    @bundle_input
    def get_user_profile(user_id):
        def camel_to_snake(name):
            return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        
        response = __use_line_api(f'https://api.line.me/v2/bot/profile/{user_id}', method="get")
        
        if response.status_code == 200:
            user_data = response.json()
            # Convert the keys to snake_case
            user_data_snake_case = {camel_to_snake(k): v for k, v in user_data.items()}
            return user_data_snake_case
        else:
            raise Exception(response.content)

    if user_id is None:
        # get all users id from chat history.
        user_ids = [ user["user_id"] for user in chat_history.find({}, {"user_id": 1, "_id":0}) ]

        # filter valid line users id.
        user_ids = [ valid_line_id for valid_line_id in user_ids if len(valid_line_id)==33 ]

        # get user data from line api
        profiles = [ get_user_profile(user_id) for user_id in user_ids ]    
    
    else:
        profile = get_user_profile(user_id)
        
        if profile is None:
            raise Exception(f'No user profile found for user_id: {user_id}')
        
        profiles = [profile]

    update_results = []

    for profile in profiles:
        query = {
            'user_id': profile["user_id"],
            'upsert' : True,
        }
        update_results.append(update(query, profile))
        
    update_results