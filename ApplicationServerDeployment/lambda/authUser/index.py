# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles api gateway authentication of user login request.
"""

import base64
import os


def lambda_handler(event, context):
    """
    Handles api gateway authentication of user login request.
    """
    credentials = os.environ['CREDENTIALS']
    headers = event.get("headers")
    username = headers.get("username")
    expected_username = base64.b64decode(credentials).decode().split(":")[0]
    if expected_username != username:
        return generate_policy("user", "Deny", event.get("methodArn"))
    return generate_policy("user", "Allow", event.get("methodArn"))


def generate_policy(principal_id: str, effect: str, resource: str):
    """
    Generates auth policy
    :param principal_id: identifier
    :param effect: either Deny or Allow
    :param resource: arn of resource
    :return: policy document
    """
    auth_response = {"principalId": principal_id}
    policy_document = {"Version": "2012-10-17"}
    statement = {"Action": "execute-api:Invoke", "Effect": effect, "Resource": [resource]}
    policy_document["Statement"] = [statement]
    auth_response["policyDocument"] = policy_document

    return auth_response
