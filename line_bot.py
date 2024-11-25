# %%
import json
import requests
import os
import utils
import uuid
from typing import Literal

utils.load_env()

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_SECRET")
BOT_VERBOSE = int(os.environ['BOT_VERBOSE'])


def __use_line_api(url_endpoint:str, data:dict=None, method:Literal['get', 'post']="post"):
    LINE_API = url_endpoint
    Authorization = f'Bearer {CHANNEL_ACCESS_TOKEN}'    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization,
        'X-Line-Retry-Key': str(uuid.uuid4())  # Generate a unique UUID
    }
    
    # Convert the dictionary to a JSON string
    data = json.dumps(data)
    
    # Send the POST request to the LINE API
    if method == 'post':
        response = requests.post(LINE_API, headers=headers, data=data)
    elif method == 'get':  # For GET requests, we don't need to pass data in the request body.
        response = requests.get(LINE_API, headers=headers, data=data)
    
    return response


def ReplyMessage(reply_token, TextMessage:list|str):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    
    answer = TextMessage
    
    if isinstance(answer, str):
        data = {
            "replyToken": reply_token,
            "messages": [
                {
                "type": "text",
                "text": answer,
                },
            ]
        }
    elif len(answer)<=5:
        data = {
            "replyToken": reply_token,
            "messages": [
                {
                "type": "text",
                "text": ans,
                } for ans in answer
            ]
        }
    elif len(answer)>5:
        raise ValueError("List of TextMessage must have length less than 5")
    
    return __use_line_api(LINE_API, data)


def ReplyMessageWithImage(reply_token, text:str, image:str):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    
    data = {
        "replyToken": reply_token,
        "messages": [
            {
            "type": "image",
            "originalContentUrl": image,
            "previewImageUrl": image
            },
            {
            "type": "text",
            "text": text,
            },
        ]
    }
    
    return __use_line_api(LINE_API, data)
    

def PushMessage(user_id:str, TextMessage:list|str):
    # Define the endpoint URL
    LINE_API = "https://api.line.me/v2/bot/message/push"

    # Define the payload (data to send in the POST request)
    if isinstance(TextMessage, str):
        data = {
            "to": user_id,  # Replace with the target user ID
            "messages": [
                {
                    "type": "text",
                    "text": TextMessage
                }
            ]
        }
    elif len(TextMessage)<=5:
        data = {
            "to": user_id,  # Replace with the target user ID
            "messages": [
                {
                    "type": "text",
                    "text": message
                }for message in TextMessage
            ]
        }
    elif len(TextMessage)>5:
        raise ValueError("List of TextMessage must have length less than 5")

    return __use_line_api(LINE_API, data)