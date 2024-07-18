"""
    Users created in AD, synched with CH
    For every new user, add him to an existing space (used for emergency notifications)
    Send welcome message, use cards
        
    Use an Admin Space to report, what?
        User added
        Message sent
    
    direct message with space description/purpose etc report in the admin space
"""

from dotenv import load_dotenv
import os
import requests
import json
from urllib.parse import urlencode, urlunparse
from datetime import timedelta, datetime

load_dotenv()
main_room_id = os.getenv("MAIN_ROOM_ID")
reporting_room_id = os.getenv("REPORTING_ROOM_ID")
webex_api_url = "https://webexapis.com/v1"


service_app_access_token = ""
# admin_token = "NTYyNDY2YzgtNjM4NC00OTdiLThmZGYtNDUyMzhkYWIwNGI2NTliMmQ5ZjItZTgz_P0A1_952e87f4-5c49-4ca1-b285-ee0570c2498c"
bot_token = os.getenv("BOT_TOKEN")

def user_in_the_space (room_id, user_email):
    path = "memberships"
    parameters = {
        "roomId": room_id,
        "max": 100,
        "personEmail": user_email
    }
    scheme, netloc, *_ = webex_api_url.replace('://', ' ').split() # '*' captures the rest, '_' indicates that it won't be used
    urlparts = (scheme, netloc, path, '', urlencode(parameters), '')
    memberships_api_url = urlunparse(urlparts)
    # memberships_api_url = webex_api_url + "memberships" + "?roomId=" + room_id + "&max=100" + "&personEmail=" + user_email
    # PENDING: pagination
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + bot_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", memberships_api_url, headers=headers, data=payload)
    print ("Get membership status code: ", response.status_code)
    
    if response.status_code == 200:
        items = json.loads(response.text)['items']
        return items
    else: print ("Error message: " + json.loads(response.text)['message'])

def get_room_name(room_id):
    rooms_api_url = webex_api_url + "/" + "rooms" + "/" + room_id# I should use urlunparse here too ?
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + bot_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", rooms_api_url   , headers=headers, data=payload)
    print ("Get room status code: ", response.status_code)
    if response.status_code == 200:
        room_name = json.loads(response.text)['title']
        return room_name
    else: print ("Error message: " + json.loads(response.text)['message'])

def get_user_name(user_email):
    path = "people"
    parameters = {
        "email": user_email
    }
    scheme, netloc, *_ = webex_api_url.replace('://', ' ').split()
    urlparts = (scheme, netloc, path, '', urlencode(parameters), '')
    people_api_url = urlunparse(urlparts)
    # people_api_url = webex_api_url + "people" + "?email=" + user_email
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + bot_token
    }
    response = requests.request("GET", people_api_url, headers=headers, data=payload)
    print ("Get username status code: ", response.status_code)
    if response.status_code == 200:
        user_name = json.loads((response.text))['items'][0]['displayName'] # always only one item ????
        return user_name
    else: print ("Error message: " + json.loads(response.text)['message'])

def add_user_to_space(room_id, user_email, is_moderator=False):      
    membebership_data = user_in_the_space(room_id, user_email)
    # if membership data is empty, add the user to the room
    if not membebership_data:
        room_name = get_room_name(room_id)
        print (f"User: {user_email} is not member of Room: {room_name}")    
        path = "memberships"
        parameters = {}
        scheme, netloc, *_ = webex_api_url.replace('://', ' ').split()
        urlparts = (scheme, netloc, path, '', urlencode(parameters), '')
        memberships_api_url = urlunparse(urlparts)
        payload = json.dumps({
            "roomId": room_id,
            "personEmail": user_email,
            "isModerator": is_moderator
        })
        headers = {
            'Authorization': 'Bearer ' + bot_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", memberships_api_url, headers=headers, data=payload)
        print ("Add user to space status code: ", response.status_code)
        if response.status_code != 200: print ("Error message: " + json.loads(response.text)['message'])

def send_message_to_space(room_id, markdown_text):
    messages_api_url = webex_api_url + "/" + "messages" # I should use urlunparse here too, I do not do it because there are no paremeters
    payload = json.dumps ({
        "roomId": room_id,
        "markdown": markdown_text,
        "text": "Original Text included markdown"
    })
    headers = {
        'Authorization': 'Bearer ' + bot_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", messages_api_url, headers=headers, data=payload)
    print ("Send message to space status code: ", response.status_code)
    if response.status_code != 200: print ("Error message: " + json.loads(response.text)['message'])

def get_tokens():
    return
    
    # return access_token, refresh_token

def refresh_tokens():
    client_id = os.getenv("SERVICE_APP_CLIENT_ID")
    client_secret = os.getenv("SERVICE_APP_CLIENT_SECRET")
    service_app_refresh_token = os.getenv("SERVICE_APP_REFRESH_TOKEN")
    
    token_url = "https://webexapis.com/v1/access_token"
    headers = {'content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=refresh_token&refresh_token={0}&client_id={1}&client_secret={2}").format(service_app_refresh_token, client_id, client_secret)
    response = requests.post(url=token_url, data=payload, headers=headers)
    print ("Send message to space status code: ", response.status_code)
    if response.status_code != 200: print ("Error message: " + json.loads(response.text)['message'])
    results = json.loads(response.text)
    access_token = results["access_token"]
    expires_in = results["expires_in"]
    print ("Access Token expires in: ", expires_in)
    print ("Remove this in production, access token: ", access_token)
    return access_token


def check_for_new_users():
    users =['test@test.com']
    return users

def main_function():
    print ('App starts')
    check_for_new_users_interval = timedelta(days=1)
    
    # service_app_access_token, service_app_refresh_token = get_tokens()
    service_app_access_token = refresh_tokens()
    new_users = check_for_new_users() # first time
    start = datetime.now()
    print ("First check:, ", start)
    while True:
        now = datetime.now()
        if now == start + check_for_new_users_interval:
            service_app_access_token = refresh_tokens()
            new_users = check_for_new_users()
            if new_users:
                add_user_to_space(main_room_id, "test@test.com")
                # report in the reporting space
                text_to_send = "User **" + "test@test.com" + "** added to Room " + reporting_room_id
                send_message_to_space(reporting_room_id, text_to_send)
                
                user_name = get_user_name('vvazquez@wxsd.us')
                welcome_message = "Hi <@personEmail:" + "vvazquez@wxsd.us" + "|" + user_name + ">" + ", welcome to Aruba"
                send_message_to_space(main_room_id, welcome_message)
                # report in the reporting space
                text_to_send = "Welcome message to **" + user_name + "** (" + "vvazquez@wxsd.us" + ") " + "sent"
                send_message_to_space(reporting_room_id, text_to_send)

                start = start + check_for_new_users_interval

if __name__ == '__main__':
    main_function()
    
# app.run("0.0.0.0", port=10060, debug=False)



