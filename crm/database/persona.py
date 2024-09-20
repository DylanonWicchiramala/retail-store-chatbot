## For database search tool
from typing import TypedDict, Optional, NotRequired, Literal
from langchain_openai import OpenAIEmbeddings
from crm.utils import load_project_db
import os


def create_persona(personas:list[dict], del_original:bool=True):
    """ this function to create persona data. if del_original, delete old data from database.
    """
    # get database
    client, db = load_project_db()  # Assumes load_project_db is defined elsewhere
    persona_collection = db["Persona"]
    
    if del_original:
        # Delete all original data from the collection
        persona_collection.delete_many({})

    if personas:
        # Insert new persona data into the collection
        persona_collection.insert_many(personas)
    
    # Close the connection to the database
    client.close()
    
    return persona_collection


def get_by_id(persona_id:str=None):
    """ this function to get customers persona data and interests into the databases.
    """
    # get database
    client, db = load_project_db()
    persona_collection = db["Persona"]
    
    # Update the document in MongoDB
    persona = persona_collection.find_one(
        {"persona_id": persona_id.strip()}
    )
    
    client.close()
    
    if persona:
        return dict(persona)
    else:
        return 'No data'


def get_all():
    client, db = load_project_db()
    persona_collection = db["Persona"]
    
    result = list(persona_collection.find())
    
    client.close()
    return result


def get_all_persona_ids():
    persona = get_all()
    
    user_ids = []
    for item in persona:
        user_ids.append(item['persona_id'])
    
    return user_ids
