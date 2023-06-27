# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import config

logger = logging.getLogger(__name__)
from response import AlexaResponse


def transform_json_input(event):
    """
    Transforms the input json to extract the parameters from the request
    param: event: input json from Alexa
    """
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


def get_bridge_offline_response(oauth_token, endpoint_id):
    """
    return a response indicating the bridge is offline
    :param oauth_token:
    :param endpoint_id:
    """
    res_error = AlexaResponse(
        name='ErrorResponse',
        payload={'type': config.DEVICE_OFFLINE_ERROR,
                 'message': config.DEVICE_OFFLINE_MESSAGE},
        token=oauth_token,
        endpointId=endpoint_id)
    if 'scope' in res_error.get()['event']['endpoint']:
        del res_error.get()['event']['endpoint']['scope']

    return res_error.get()
