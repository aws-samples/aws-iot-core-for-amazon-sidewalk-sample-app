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

def get_all_filenames(bucket_name, prefix=''):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Extract filenames from the response
    if not prefix:
        filenames = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].count('/') == prefix.count('/')]
    else:
        filenames = [obj['Key'] for obj in response.get('Contents', []) if not obj['Key'].endswith('/')]

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

        # Get all filenames in the root of the bucket
        all_filenames = get_all_filenames(OTA_S3_BUCKET_NAME)

        # Get filenames in the 'current' folder if it exists
        current_folder_filenames = get_all_filenames(OTA_S3_BUCKET_NAME, 'current-firmware/')

        # Extract the current firmware file name (if exists)
        current_firmware_filename = None
        if current_folder_filenames:
            current_firmware_filename = current_folder_filenames[0]

        # Prepare the output
        output = {
            'fileNames': all_filenames,
            'currentFirmwareFileName': current_firmware_filename
        }

        return {
            'statusCode': 200,
            'body': json.dumps(output)
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
