import crm.database.chat_history as chat_history
import datetime
from collections import defaultdict
from crm.utils import load_project_db

user_id = "U9ba421923ad9e8b980900eb3eb6118d6"

def get_user_chat_times(user_id):
    history = chat_history.load_chat_history(user_id=user_id, load_raw=True)["chat_history"]

    chat_time = []

    # extract user chat time 
    for i in range(len(history)):
        # extract only user chat
        if i%2==0:
            chat_time.append(history[i]['timestamp'])
            
    return chat_time
            

def analyze_user_active_time(chat_time:list[datetime.datetime]):
    # Initialize a defaultdict for holding the results
    result = defaultdict(lambda: {"frequency": 0, "total_seconds": 0})
    
    # Iterate over each timestamp
    for ts in chat_time:
        dt = ts
        day_of_week = dt.strftime("%A")  # Get the day of the week as a string (e.g., 'Monday')
        
        # Update frequency and total seconds (for calculating the average time)
        result[day_of_week]["frequency"] += 1
        result[day_of_week]["total_seconds"] += dt.hour * 3600 + dt.minute * 60 + dt.second
    
    # Calculate average time for each day of the week
    for day, data in result.items():
        if data["frequency"] > 0:
            avg_seconds = data["total_seconds"] // data["frequency"]
            avg_time = datetime.timedelta(seconds=avg_seconds)
            result[day]["average_time"] = str(avg_time)  # Convert timedelta to string (e.g., '10:30:00')
        else:
            result[day]["average_time"] = "00:00:00"  # If no timestamps, default average to '00:00:00'

        # Remove the total_seconds field, as it's no longer needed
        del result[day]["total_seconds"]
    
    result = dict(result)  # Convert defaultdict back to a regular dictionary
    result = dict(sorted(result.items(), key=lambda x: x[1]["frequency"], reverse=True))
    return result


def save_user_active_time(user_id:str):
    
    chat_time = get_user_chat_times(user_id=user_id)
    active_time = analyze_user_active_time(chat_time)

    # get most active time
    most_active_time = dict(list(active_time.items())[:2])

    active = []
    for days, value in most_active_time.items():
        active.append([days.lower(), value['average_time']])
        
    client, db = load_project_db()
    costomer_collection = db["Customer"]

    costomer_collection.update_one(
        {"user_id": user_id},
        {"$set": 
            {
                "active_time":active
            }
        },
        upsert=True  # Create a new document if no matching document is found
    )

    client.close()


