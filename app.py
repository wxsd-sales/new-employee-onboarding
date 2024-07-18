"""
    Users created in AD, synched with CH
    For every new user, add him to an existing space (used for emergency notifications)
    Send welcome message, use cards. New requeriment: Welcome should be a 1:1 message
        
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

load_dotenv()
main_room_id = os.getenv("MAIN_ROOM_ID")
reporting_room_id = os.getenv("REPORTING_ROOM_ID")
webex_api_url = "https://webexapis.com/v1"

service_app_refresh_token = os.getenv("SERVICE_APP_REFRESH_TOKEN")
bot_token = os.getenv("BOT_TOKEN")

org_id = "952e87f4-5c49-4ca1-b285-ee0570c2498c"

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
    path = 'rooms'
    rooms_api_url = webex_api_url + "/" + path + "/" + room_id # Should I use urlunparse here too ? there are no parameters
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
    # check if user is already a member of the space
    membebership_data = user_in_the_space(room_id, user_email)
    # if membership data is empty, add the user to the room
    if not membebership_data:
        room_name = get_room_name(room_id)
        print (f"User: {user_email} is not member of Room: {room_name}")    
        path = "memberships"
        
        # parameters = {}
        # scheme, netloc, *_ = webex_api_url.replace('://', ' ').split()
        # urlparts = (scheme, netloc, path, '', urlencode(parameters), '')
        # memberships_api_url = urlunparse(urlparts)
        
        memberships_api_url = webex_api_url + "/" + path # Should I use urlunparse here too ? there are no parameters
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
    path = "messages"
    messages_api_url = webex_api_url + "/" + path # I should use urlunparse here too, I do not do it because there are no paremeters
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

def send_message_to_person(person_email, markdown_text):
    path = "messages"
    messages_api_url = webex_api_url + "/" + path # I should use urlunparse here too, I do not do it because there are no paremeters
    payload = json.dumps ({
        "toPersonEmail": person_email,
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

def refresh_tokens():
    client_id = os.getenv("SERVICE_APP_CLIENT_ID")
    client_secret = os.getenv("SERVICE_APP_CLIENT_SECRET")   
    token_url = "https://webexapis.com/v1/access_token"
    headers = {'content-type':'application/x-www-form-urlencoded'}
    # I am not sure if I can use urlencode/urlunparse here. Params are inside the body
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

def scim_search_users (access_token):
    # SCIM API URl is not 'under' https://webexapis.com/v1
    scim_base_url = 'https://webexapis.com/identity/scim/' + org_id + '/v2/Users/'
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", scim_base_url, headers=headers, data=payload)
    print ("SCIM Search users status code: ", response.status_code)
    
    if response.status_code == 200:
        items = json.loads(response.text)['Resources']
        return items
    else: print ("Error message: " + json.loads(response.text)['message'])

def check_for_new_users():
   
    # Use SCIM 2 API
    # Avoid listing all users would be a good practice: get only new users using filters
    #    "urn:scim:schemas:extension:cisco:webexidentity:2.0:User": {
    #            "meta": {
    #                "organizationId": "952e87f4-5c49-4ca1-b285-ee0570c2498c"
    #            },
    #            "userNameType": "email",
    #                "New-user"
    #           "extensionAttribute1": [
    #            ]
    #        }
    # With filters, I am able to get meta.organizationId but not extensionAttribute1
    # Let's then get all the users and use only the ones with the attribute
    
    access_token = refresh_tokens() # I pass token to reuse scim_search_users function to make it re-usable
    all_users = scim_search_users(access_token)
    key_to_find = 'extensionAttribute1'
    value_to_find = 'New-user'
    new_users = []
    # the key 'extensionAttribute1' is not always present
    # I am not sure if I can search it doing comprehension, Y try normal for
    for user in all_users:
        if key_to_find in user["urn:scim:schemas:extension:cisco:webexidentity:2.0:User"]:
            if user["urn:scim:schemas:extension:cisco:webexidentity:2.0:User"][key_to_find][0] == value_to_find:
                new_users.append(user)
    return new_users

def main_function():
    print ('App starts')
    new_users = check_for_new_users()
    if new_users:
        for user in new_users:
            user_email = user['userName']
            add_user_to_space(main_room_id, user_email)
            
            # report in the reporting space
            text_to_send = "User **" + user_email + "** added to Room " + reporting_room_id
            send_message_to_space(reporting_room_id, text_to_send)
            
            # send 1:1 message to new empployee
            user_name = get_user_name(user_email)
            welcome_message = "Hi " + user_name + ", welcome to Aruba" # Mentions are not supported in 1-to-1 rooms
            # welcome_message = "Hi <@personEmail:" + user_email  +  ">" + ", welcome to Aruba"
            # one exmaple I found: welcome_message = "Hi <@personEmail:" + user_email + "|" + user_name + ">" + ", welcome to Aruba"
            send_message_to_person(user_email,welcome_message)
            
            # report in the reporting space
            text_to_send = "Welcome message to **" + user_name + "** (" + user_email + ") " + "sent"
            send_message_to_space(reporting_room_id, text_to_send)
if __name__ == '__main__':
    main_function()
