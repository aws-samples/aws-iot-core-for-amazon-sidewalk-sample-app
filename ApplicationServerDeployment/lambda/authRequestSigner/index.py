# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Authenticates user credentials and generates jwt token.
"""

import base64
import json
import jwt
import os


def lambda_handler(event, context):
    """
    Authenticates user credentials and generates jwt token.
    """
    credentials = os.environ['CREDENTIALS']
    user_creds = json.loads(event.get("body"))
    username = user_creds.get("username")
    password = user_creds.get("password")
    auth_bytes = f'{username}:{password}'.encode('ascii')
    auth_string = base64.b64encode(auth_bytes).decode('ascii')
    if auth_string != credentials:
        return {
            "statusCode": 401,
            "body": "username or password are incorrect",
        }

    token = jwt.encode({"name": username}, credentials, algorithm="HS256")
    return {
        "statusCode": 200,
        "body": token
    }
