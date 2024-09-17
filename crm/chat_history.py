import os
import crm.utils as utils
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain_core.messages import (
    AIMessage, 
    HumanMessage,
)
from datetime import datetime, timedelta

utils.load_env()

# Connect to the "RetailStore" database
client, db = utils.load_project_db()
history = db["Chat History"]
    
    
def load_chat_history(chat_history:list=[], user_id:str=""):
    query = history.find_one({"user_id": user_id})
    if query is None:
        query = {
            "user_id": user_id,
            "chat_history": [],
        }
        history.insert_one(query)

    for i, msg in enumerate(query["chat_history"]):
        msg = msg['content']
        chat_history.append(
            AIMessage(msg) if i % 2 == 1 else HumanMessage(msg)
        )
    
    return chat_history