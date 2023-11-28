# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles that fetches all the files present in OTA S3 bucket.
"""

import os
import boto3
import json
import traceback
from typing import Final

OTA_S3_BUCKET_NAME: Final = os.environ.get('OTA_S3_BUCKET_NAME')

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()

def get_all_filenames(bucket_name):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)

    # Extract filenames from the response
    filenames = [obj['Key'] for obj in response.get('Contents', [])]

    return filenames



def lambda_handler(event, context):
    """
    Handles events triggered by incoming ota actions.
    """
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Get the files names from s3 bucket
        # ---------------------------------------------------------------
        print(f'Received event: {event}')
        filenames = get_all_filenames(OTA_S3_BUCKET_NAME)

        return {
            'statusCode': 200,
            'body': json.dumps(filenames)
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
