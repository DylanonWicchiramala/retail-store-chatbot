# %%
from crm.database import ads, customer_data
import line_bot
from datetime import datetime
import schedule
import threading
import time
from typing import Literal


def push_personal_ads(user_id:str=None, push_all:bool=False):
    def send_ad(user_id:str):
        if not ad_content["time_displayed"]:

            response = line_bot.PushMessage(user_id=user_id, TextMessage=ad_content['content'])
            
            if response.status_code==200:
                ads.set(user_id=user_id, time_displayed=datetime.now())
                
            return response
    
    if user_id:
        return send_ad(user_id)
    
    if push_all:
        ads = ads.get_all_ads()

        for ad_content in ads:
            user_id = ad_content['user_id']
            send_ad(user_id=user_id)


def schedule_push_personal_ads(
    user_id:str=None, 
    push_all:bool=False, 
    days:Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]="friday", 
    at:str="09:30", 
    timezone:str="Asia/Bangkok"):
    
    """Schedule push_personal_ads to run every Date in week"""
    schedule_every = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
    }
    
    push_ads = lambda: push_personal_ads(user_id, push_all)
    
    schedule_every[days].at(at, timezone).do(push_ads)
    

def schedule_push_personal_ads_by_user_active_time(user_id:str=None, push_all:bool=False):
    
    def push_ads(user_id):
        personal = customer_data.get_customer_information_by_id(user_id=user_id)
        active_times = personal.get('active_time', [])
        if len(active_times)>0:
            for active_time in active_times:
                days, time = active_time
                schedule_push_personal_ads(user_id=user_id, days=days, at=time)
        # if no user active time data found
        else:
            schedule_push_personal_ads(user_id=user_id)
            
    if user_id:
        push_ads(user_id=user_id)

    if push_all:
        ads = ads.get_all_ads()

        for ad_content in ads:
            user_id = ad_content['user_id']
            push_ads(user_id=user_id)


def schedule_run_pending():
    while True:
        schedule.run_pending()  # Check if scheduled task is due
        time.sleep(60)  # Wait before checking again
        
        


def run_in_threads():
    def run():
        schedule_push_personal_ads_by_user_active_time(user_id="U9ba421923ad9e8b980900eb3eb6118d6")
        schedule_run_pending()
        
    # Create a thread for the scheduling function
    schedule_thread = threading.Thread(target=run)
    schedule_thread.daemon = True  # Daemon threads exit when the main program exits
    schedule_thread.start()


if __name__ == "__main__":
    run_in_threads()