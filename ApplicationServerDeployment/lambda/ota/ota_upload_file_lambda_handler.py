# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

import base64
import os
import boto3
import json
import traceback
from typing import Final

s3 = boto3.client('s3')
# TODO - Replace with S3_Client

OTA_S3_BUCKET_NAME: Final = os.environ.get('OTA_S3_BUCKET_NAME')


def lambda_handler(event, context):
    """
    Handles events triggered by incoming ota actions.
    """
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Read its metadata.
        # Decode payload data.
        # ---------------------------------------------------------------
        if type(event) == dict:
            event = json.dumps(event)

        event = json.loads(event)
        print(f'Received event: {event}')
        body = event.get('body', {})
        print(f'Received request body: {body}')
        if body is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Body field is missing')
            }
        if type(body) == dict:
            json_body = body
        else:
            json_body = json.loads(body)

        # Assuming the file is sent as a base64-encoded string in the 'file' field of the request
        file_content = json_body.get("file")
        file_name_with_ext = json_body.get("filename")

        if file_content:
            # Decode base64 content to get the original file content
            decoded_file_content = base64.b64decode(file_content)
            print(f'First 100 characters of the file content: {decoded_file_content[:100]}')
            s3.put_object(Body=decoded_file_content, Bucket=OTA_S3_BUCKET_NAME, Key=file_name_with_ext)

        return {
            'statusCode': 200,
            'body': json.dumps('File received and saved to S3 successfully!')
        }
    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
