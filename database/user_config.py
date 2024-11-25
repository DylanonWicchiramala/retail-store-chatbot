from typing import TypedDict
import utils
import database

utils.load_env()

COLLECTION_NAME = "User Config"

DEFAULT_USER_CONFIG = {
    "enable_bot_response": True
}

class UserConfigSchema(TypedDict):
    user_id: str
    enable_bot_response: bool = True

class UpdateSchema(TypedDict):
    enable_bot_response: bool = True

class QuerySchema(UserConfigSchema):
    _id:str
    upsert:bool


def __add(data: UserConfigSchema) -> dict:
    # connect db
    client, db = database.load_db()
    collection = db[COLLECTION_NAME]
    
    # Insert the order into the collection
    inserted_id = collection.insert_one(data).inserted_id
    
    # Retrieve the newly inserted document
    result = collection.find_one({"_id": inserted_id})
    
    client.close()
    return result


def __update(query:QuerySchema, data: UserConfigSchema) -> dict:
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
    return __get(query)


def __get(query:QuerySchema, *query_args, **query_kwargs) -> list[dict]:
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


def set(user_id:str, config:UpdateSchema=DEFAULT_USER_CONFIG)->dict:
    old_config = __get({"user_id": user_id})
    new_config = dict(**config, user_id=user_id)
    
    if len(old_config)==0:
        return __update({"user_id":user_id, "upsert":True}, new_config)
    else:
        return __update({"user_id": user_id, "upsert":False}, new_config)
        
        