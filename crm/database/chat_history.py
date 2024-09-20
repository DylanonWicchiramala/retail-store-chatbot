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
    

def load_chat_history(chat_history: list = [], after: datetime = None, user_id: str = "", load_raw: bool = False):
    """
    Load chat history from the database for a given user. 
    Optionally filter messages by timestamp if 'after' is provided.
    
    Parameters:
    - chat_history (list): List to append the chat history.
    - after (datetime): Filter to load messages after a specific timestamp.
    - user_id (str): The user ID to load chat history for.
    - load_raw (bool): If True, returns raw data from the database.
    
    Returns:
    - chat_history (list): A list of AIMessage and HumanMessage objects.
    """
    # Get the database (assuming it's already connected)
    client, db = utils.load_project_db()  # This is where you'd connect to the MongoDB
    history = db["Chat History"]

    if load_raw:
        return history.find_one({"user_id": user_id})

    else:
        query = history.find_one({"user_id": user_id})
        if query is None:
            query = {
                "user_id": user_id,
                "chat_history": [],
            }
            history.insert_one(query)
        
        # Filter messages by the 'after' timestamp
        for i, msg in enumerate(query["chat_history"]):
            timestamp = msg.get("timestamp")
            
            # Only process messages that have a timestamp and are after the provided 'after' datetime
            if timestamp and after:
                msg_time = datetime.fromisoformat(timestamp[:-1])  # Convert ISO format to datetime
                if msg_time <= after:
                    continue  # Skip messages older than the 'after' timestamp

            # Append filtered messages to chat history
            content = msg['content']
            chat_history.append(
                AIMessage(content) if i % 2 == 1 else HumanMessage(content)
            )
    
    client.close()  # Close database connection
    return chat_history