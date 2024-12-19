import traceback
from flask import Flask, redirect, render_template, request, abort, jsonify, url_for
from flask_cors import CORS
import json
import requests
import os
from chatbot_multiagent import submitUserMessage
from database import load_db, user_config, user_profile
import utils
import line_bot
import crm

utils.load_env()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_SECRET")
BOT_VERBOSE = int(os.environ['BOT_VERBOSE'])

@app.route('/', methods=['POST', 'GET'])
async def webhook():
    if request.method == 'POST':
        payload = request.json
        # Log the entire payload for debugging
        app.logger.info(f"Received payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Check Event (can be multiple event)
            for event in payload['events']:
                user_id = event["source"]["userId"]
                # set user profile and default config
                user_profile.update_pipeline(user_id)
                # user config default setting
                if not len(user_config.__get({"user_id":user_id})):
                    user_config.set(user_id)
                
                
                # Get reply token (reply in 1 min)
                reply_token = event['replyToken']     
                bot_response_enable = user_config.__get({"user_id":user_id})[0]['enable_bot_response']
                if event['type'] == 'message' and bot_response_enable:
                    user_message = event["message"]["text"]
                    # Model Invoke
                    response = submitUserMessage(user_message, user_id=user_id, keep_chat_history=True, return_reference=False, verbose=BOT_VERBOSE)
                    response = utils.format_bot_response(response, markdown=False)
                    line_bot.ReplyMessage(reply_token, response)
            
            return request.json, 200
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            app.logger.error(f"Error: {e}\nTraceback: {error_traceback}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "method not allowed"}), 400
        
        
@app.route('/test', methods=['POST', 'GET'])
def chatbot_test():
    try:
        user_message = request.json.get('message', '')
        
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": f"{e}"}), 500

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = submitUserMessage(user_message, user_id="test", keep_chat_history=False, return_reference=True, verbose=BOT_VERBOSE)
        response = utils.format_bot_response(response, markdown=False)
        
        if isinstance(response, list):
            response = response[0]
        
        return jsonify({"response": response})

    except Exception as e:
        error_traceback = traceback.format_exc()
        app.logger.error(f"Error: {e}\nTraceback: {error_traceback}")
        return jsonify({"error": f"{e}"}), 500
        
        
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Perform any necessary checks here (e.g., database connection, etc.)
        # For now, we just return a simple success message
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        app.logger.error(f"Error: {e}\nTraceback: {error_traceback}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
    

@app.route('/run-automate', methods=['GET'])
def run_automate():
    try:
        crm.run_pipelines()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        error_traceback = traceback.format_exc()
        app.logger.error(f"Error: {e}\nTraceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500


@app.route('/admin-console')
async def admin_console():
    # Get user profiles from the database.
    client, db = load_db()

    user_profile = db['User Profile']

    users = user_profile.aggregate([
        {
            '$lookup': {
                'from': 'User Config',          # Name of the collection to join with
                'localField': 'user_id',        # Field in the `User Profile` collection
                'foreignField': 'user_id',      # Field in the `User Config` collection
                'as': 'User Config'             # Alias for the output array
            }
        },
        {
            '$unwind': {                       # Unwind the joined array to create a flat structure
                'path': '$User Config',
                'preserveNullAndEmptyArrays': True  # Keeps users without matching 'User Config'
            }
        },
        {
            '$replaceRoot': {                  # Merge the 'User Config' data to the top level
                'newRoot': {
                    '$mergeObjects': ['$User Config', '$$ROOT']
                }
            }
        },
        {
            '$project': {                     # Remove the nested 'User Config' after merging
                'User Config': 0
            }
        }
    ])

    users = list(users)

    client.close()

    # Now `users` will be a list of flat dictionaries containing fields from both collections.
    
    return render_template('admin_console.html', users=users)


@app.route('/change-store-name/<name>', methods=['POST'])
async def change_store(name):
    """ change env. STORE_NAME to name
    """
    try:
        os.environ['STORE_NAME'] = name
        return jsonify({"status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/toggle/<user_id>', methods=['POST'])
async def toggle_user(user_id):
    # Get the current state from the form.
    enable_bot_response = request.form.get('enable_bot_response') == 'on'
    
    # Update the user configuration in the database.
    user_config.set(user_id, {"enable_bot_response": enable_bot_response})
    
    return redirect(url_for('admin_console'))    


# Run the Flask app
if __name__ == '__main__':
    app.run(port=8080, debug=True)