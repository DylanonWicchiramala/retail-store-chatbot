from datetime import datetime
from pymongo import MongoClient
import crm.utils as utils

# Load the MongoDB client and database
client, db = utils.load_project_db()
ads_collection = db["Personalized Ads"]

def set(user_id: str, content:str=None, time_create:datetime=None, time_displayed:datetime=None):
    """
    Pushes new data into the 'Personalized Ads' collection.

    Parameters:
    - user_id (str): The ID of the user.
    - content (str): The content to be added to the database.
    - is_ads_displayed (bool): Whether ads have been displayed to the user.
    """
    data = {
        "time_displayed": time_displayed, 
        }
    if content:
        data['content'] = content
    if not time_displayed:
        data['time_create'] = time_create if time_create else datetime.now()
    
    # Insert or update the user's record
    result = ads_collection.update_one(
        {"user_id": user_id},
        {
            "$set": data,
        },
        upsert=True  # Insert if it doesn't exist
    )
    return result


def get(user_id: str):
    """
    Retrieves data from the 'Personalized Ads' collection for a specific user.

    Parameters:
    - user_id (str): The ID of the user whose data will be fetched.

    Returns:
    - dict: The document associated with the user.
    """
    timestamp = datetime.now()
    
    data = ads_collection.find_one({"user_id": user_id})
    
    set(user_id=user_id, time_displayed=timestamp)
    return data