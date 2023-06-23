import base64
import json
import logging
import requests
import config
logger = logging.getLogger(__name__)
import os
from response import AlexaResponse
import jwt
import time

def get_device_info():
    user_devices = get_user_devices()

    user_device = user_devices[0]
    epoch_timestamp = user_device['last_uplink']
    device_id = user_device['wireless_device_id']
    is_device_online = epoch_timestamp > time.time() - 15
    current_states=user_device
    return is_device_online,device_id, current_states


def change_device_state(device_id,dsn, state):
    url = get_base_url()+'/'

    payload = json.dumps({
        "command": "DEMO_APP_ACTION_REQ",
        "deviceId": str(device_id),
        "ledId": int(dsn),
        "action": str(state)
    })
    headers = {
        'authorizationtoken': "Basic " + get_encoded_token(),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        logger.error("Error in changing device state from Sidewalk API")
        return False
    return True

def transform_json_input(event):
    oauth_token = event['directive']['endpoint']['scope']['token']
    endpoint_id = event['directive']['endpoint']['endpointId']
    correlation_token = event['directive']['header']['correlationToken']
    if "cookie" in event['directive']['endpoint']:
        cookie = event['directive']['endpoint']['cookie']
    else:
        cookie = {}
    if 'payload' in event['directive']:
        payload = event['directive']["payload"]
    else:
        payload = {}
    return oauth_token, endpoint_id, correlation_token, cookie, payload
def get_base_url():
    API_BASE_URL = os.environ.get('CDN_URL', '')

    if API_BASE_URL == "":
        logger.error("Error in getting API URL from environment variable")
        return []
    API_BASE_URL = "https://" + API_BASE_URL
    API_BASE_URL = API_BASE_URL + "/api"
    return API_BASE_URL
def get_user_devices():
    devices_url=get_base_url()+ "/devices"

    headers = {
        'authorizationtoken': "Basic " + get_encoded_token(), }
    response = requests.get(devices_url, headers=headers)
    if response.status_code != 200:
        logger.error("Error in getting devices from Sidewalk API")
        user_devices = []
    else:
        user_devices = response.json()

        return user_devices

def get_device_temp(device_id):
    temp_url=get_base_url()+ "/api/measurements/"+device_id

    headers = {
        'authorizationtoken': "Basic " + get_encoded_token(), }
    response = requests.get(temp_url, headers=headers)
    if response.status_code != 200:
        logger.error("Error in getting devices from Sidewalk API")
        temp = None
    else:
        temp_wrapper = response.json()
        temp_wrapper=temp_wrapper[0]
        if temp_wrapper['wireless_device_id'] == device_id:
            temp=temp_wrapper['value']

        return temp

def get_encoded_token():
    """
    encode user payload as a jwt
    :param user:
    :return:
    """
    base64_encoded_creds=os.environ.get('CREDENTIALS', '')
    if base64_encoded_creds == "":
        logger.error("Error in getting base64_encoded credentials from environment variable")
        return []
    creds=base64.b64decode(base64_encoded_creds).decode().split(":")
    jwt_encoded_token = jwt.encode(payload={"name": creds[0]},
                                   key=base64_encoded_creds,
                                   algorithm="HS256")

    return jwt_encoded_token

def get_bridge_offline_response(oauth_token, endpoint_id):
    res_error = AlexaResponse(
        name='ErrorResponse',
        payload={'type': config.DEVICE_OFFLINE_ERROR,
                 'message': config.DEVICE_OFFLINE_MESSAGE},
        token=oauth_token,
        endpointId=endpoint_id)
    if 'scope' in res_error.get()['event']['endpoint']:
        del res_error.get()['event']['endpoint']['scope']

    return res_error.get()