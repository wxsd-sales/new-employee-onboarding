from dotenv import load_dotenv
import os
import requests
import json
import urllib.parse
import traceback

load_dotenv()
service_app_refresh_token = os.getenv("SERVICE_APP_REFRESH_TOKEN")
bot_token = os.getenv("BOT_TOKEN")
main_room_id = os.getenv("MAIN_ROOM_ID")
reporting_room_id = os.getenv("REPOTING_ROOM_ID")
webex_api_url = "https://webexapis.com/v1"
org_id = "952e87f4-5c49-4ca1-b285-ee0570c2498c"

headers = { 
    'Authorization': 'Bearer ' + bot_token,
    'Content-Type': 'application/json'
}

def user_in_the_space (room_id, user_email):
    # You need to encode URL paratemeters properly, otherwise address with '+' will fail, for example
    encoded_email = urllib.parse.quote(user_email)
    memberships_api_url = "{0}/memberships?roomId={1}&personEmail={2}&max=100".format(webex_api_url, room_id, encoded_email)
    # memberships_api_url = webex_api_url + "memberships" + "?roomId=" + room_id + "&max=100" + "&personEmail=" + user_email
    # PENDING: pagination

    try:
        response = requests.request("GET", memberships_api_url, headers=headers)
        print ("User in the space GET status code: ", response.status_code)
        items = json.loads(response.text)['items']
        return items
    except Exception as e:
        traceback.print_exc()
    """
    if response.status_code == 200:
        items = json.loads(response.text)['items']
        return items
    else: print ("Error message: " + json.loads(response.text)['message']) # if you do it like this, this line could not be loaded depending on the error, 
    script fails after the GET request. For example if the webex_api_url is not well formed
    """ 

def get_room_name(room_id):
    rooms_api_url = "{0}/rooms/{1}".format(webex_api_url, room_id)
    try:
        response = requests.request("GET", rooms_api_url, headers=headers)
        print ("Get room status code: ", response.status_code)
        room_name = json.loads(response.text)['title']
        return room_name
    except Exception as e:
        traceback.print_exc()

def get_user_name(user_email):
    # people_api_url = webex_api_url + "people" + "?email=" + user_email
    encoded_email = urllib.parse.quote(user_email)
    people_api_url = "{0}/people?email={1}".format(webex_api_url, encoded_email)
    try:
        response = requests.request("GET", people_api_url, headers=headers)
        print ("Get username status code: ", response.status_code)
        user_name = json.loads((response.text))['items'][0]['displayName'] # PENDING: always only one item ????
        return user_name
    except Exception as e:
        traceback.print_exc()

def add_user_to_space(room_id, user_email, is_moderator=False):      
    # check if user is already a member of the space
    membership_data = user_in_the_space(room_id, user_email)
    # if membership data is empty, add the user to the room
    if not membership_data:
        room_name = get_room_name(room_id)
        print (f"User: {user_email} is not member of Room: {room_name}")    
        memberships_api_url = webex_api_url + "/" + "memberships"
        payload = json.dumps({
            "roomId": room_id,
            "personEmail": user_email,
            "isModerator": is_moderator
        })
        try: 
            response = requests.request("POST", memberships_api_url, headers=headers, data=payload)
            print ("Add user to space status code: ", response.status_code)
        except Exception as e:
            traceback.print_exc()

def send_message_to_space(room_id, markdown_text):
    messages_api_url = webex_api_url + "/" + "messages"
    payload = json.dumps ({
        "roomId": room_id,
        "markdown": markdown_text,
        "text": "Original Text included markdown"
    })
    try:
        response = requests.request("POST", messages_api_url, headers=headers, data=payload)
        print ("Send message to space status code: ", response.status_code)
    except Exception as e:
        traceback.print_exc()

def send_message_to_person(person_email, markdown_text):
    messages_api_url = webex_api_url + "/" + "messages"
    payload = json.dumps ({
        "toPersonEmail": person_email,
        "markdown": markdown_text,
        "text": "Original Text included markdown"
    })
    try:
        response = requests.request("POST", messages_api_url, headers=headers, data=payload)
        print ("Send message to space status code: ", response.status_code)
    except Exception as e:
        traceback.print_exc()

def refresh_tokens():
    client_id = os.getenv("SERVICE_APP_CLIENT_ID")
    client_secret = os.getenv("SERVICE_APP_CLIENT_SECRET")   
    token_url = "https://webexapis.com/v1/access_token"
    refresh_headers = {'content-type':'application/x-www-form-urlencoded'}
    # I am not sure if I can use urlencode/urlunparse here. Params are inside the body
    payload = ("grant_type=refresh_token&refresh_token={0}&client_id={1}&client_secret={2}").format(service_app_refresh_token, client_id, client_secret)
    try:
        response = requests.post(url=token_url, data=payload, headers=refresh_headers)
        print ("Send message to space status code: ", response.status_code)
        results = json.loads(response.text)
        access_token = results["access_token"]
        expires_in = results["expires_in"]
        print ("Access Token expires in: ", expires_in)
        print ("Remove this in production, access token: ", access_token)
        return access_token
    except Exception as e:
        traceback.print_exc()
        
def scim_search_users (access_token):
    # SCIM API URl is not 'under' https://webexapis.com/v1
    scim_base_url = 'https://webexapis.com/identity/scim/' + org_id + '/v2/Users/'
    scim_search_headers = { 
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("GET", scim_base_url, headers=scim_search_headers)
        print ("SCIM Search users status code: ", response.status_code)
        items = json.loads(response.text)['Resources']
        return items
    except Exception as e:
        traceback.print_exc()      

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
    key_to_find = 'postalCode'
    value_to_find = 'E'
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
            
            # send 1:1 message to new employee
            user_name = get_user_name(user_email)
            welcome_message = "Hi " + user_name + ", welcome to Aruba" # Mentions are not supported in 1-to-1 rooms
            # welcome_message = "Hi <@personEmail:" + user_email  +  ">" + ", welcome to Aruba"
            # one example I found: welcome_message = "Hi <@personEmail:" + user_email + "|" + user_name + ">" + ", welcome to Aruba"
            send_message_to_person(user_email,welcome_message)
            
            # report in the reporting space
            text_to_send = "Welcome message to **" + user_name + "** (" + user_email + ") " + "sent"
            send_message_to_space(reporting_room_id, text_to_send)
if __name__ == '__main__':
    main_function()
