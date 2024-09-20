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


def get_persona(user_id:str=None, persona_id:str=None):
    pass