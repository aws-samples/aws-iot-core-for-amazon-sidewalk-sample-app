# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Authenticates user jwt token.
"""

import base64

import jwt
import os


def lambda_handler(event, context):
    """
    Authenticates user jwt token.
    """
    credentials = os.environ['CREDENTIALS']
    authorization_token = event.get("authorizationToken")
    status = "unauthorized"
    try:
        access_token = authorization_token.split(" ")[1]
        decoded = jwt.decode(access_token, credentials, algorithms="HS256")
        creds = base64.b64decode(credentials).decode().split(":")
        expected_user = creds[0]
        received_user = decoded.get("name")
        if expected_user == received_user:
            status = "allow"
    except Exception as e:
        print(e)

    if status == "allow":
        return generate_policy("user", "Allow", event.get("methodArn"))
    else:
        return generate_policy("user", "Deny", event.get("methodArn"))


def generate_policy(principal_id: str, effect: str, resource: str):
    """
    Generates auth policy for all api gateway resources
    :param principal_id: identifier
    :param effect: either Deny or Allow
    :param resource: arn of resource
    :return: policy document
    """
    auth_response = {"principalId": principal_id}
    policy_document = {"Version": "2012-10-17"}
    resources = resource.split("dev", 1)[0] + "*"
    statement = {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resources}
    policy_document["Statement"] = [statement]

    auth_response["policyDocument"] = policy_document

    return auth_response
