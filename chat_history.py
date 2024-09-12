import os
import utils
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain_core.messages import (
    AIMessage, 
    HumanMessage,
)
from datetime import datetime, timedelta

utils.load_env()

mongo = os.environ.get('MONGODB_PASS')
uri = f"mongodb+srv://dylan:{mongo}@cluster0.wl8mbpy.mongodb.net/"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["FeasibilityAnalysis"]
history = db["Chat History"]


def save_chat_history(bot_message:str, human_message:str, user_id: str = "test"):
    timestamp = datetime.now()

    # Update the document in MongoDB
    history.update_one(
        {"user_id": user_id},
        {"$push": {
            "chat_history": {
                "$each": [
                    {"content": human_message, "timestamp": timestamp},
                    {"content": bot_message, "timestamp": timestamp}
                ]
            }
        }},
        upsert=True  # Create a new document if no matching document is found
    )
    
    
def load_chat_history(chat_history:list=[], user_id:str="test"):
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


def delete_chat_history(user_id=None, time_before=None, delete_all=False):
    """
    Deletes chat history from the MongoDB collection.

    Parameters:
    - user_id (str, optional): The user_id whose chat history should be deleted.
    - time_before (datetime, optional): Deletes chat history before this datetime.
    - delete_all (bool, optional): If True, deletes all chat history for the user.

    Returns:
    - UpdateMany: The result of the update operation.
    """
    query = {}

    # If deleting all chat history for a specific user or all users
    if delete_all:
        if user_id:
            query = {'user_id': user_id}
        else:
            query = {}

        # Remove entire chat history field
        return history.update_many(query, {'$unset': {'chat_history': 1}})

    # If filtering by user and time_before
    if user_id:
        query['user_id'] = user_id

    if time_before:
        query['chat_history.timestamp'] = {'$lt': time_before}
        # Remove specific entries from the chat history array based on the timestamp
        return history.update_many(query, {'$pull': {'chat_history': {'timestamp': {'$lt': time_before}}}})
    
    return history.delete_many(query)  # Delete documents matching the query


# delete chat history older than 30 days.
delete_chat_history(time_before=datetime.now() - timedelta(days=3))
delete_chat_history(user_id="test")