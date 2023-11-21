# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

import base64
import boto3
import json
import traceback
from datetime import datetime, timezone
from typing import Final

import time_utils
from device import Device
from measurement import Measurement

OTA_S3_BUCKET_NAME: Final = "sidewalk-ota-src"

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()

s3 = boto3.client('s3')
# TODO - Replace with S3_Client



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
        print(f'Received event: {event}')

        # Assuming the file is sent as a base64-encoded string in the 'file' field of the request
        file_content = event['body'].get('file', None)
        file_name_with_ext = event['body'].get('filename')

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
