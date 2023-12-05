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

import os
import json
import traceback
import boto3

OTA_S3_BUCKET_NAME = os.environ.get('OTA_S3_BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Retrieve fileName from the request body
        request_body = json.loads(event['body'])
        file_name = request_body.get('fileName')

        # Ensure the fileName is provided
        if not file_name:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: fileName is required')
            }

        s3 = boto3.client('s3')

        # Delete all files in sidewalk-ota-src/current-firmware/
        current_firmware_prefix = 'current-firmware/'
        current_firmware_objects = s3.list_objects_v2(Bucket=OTA_S3_BUCKET_NAME, Prefix=current_firmware_prefix)

        if 'Contents' in current_firmware_objects:
            objects_to_delete = [{'Key': obj['Key']} for obj in current_firmware_objects['Contents']]
            s3.delete_objects(Bucket=OTA_S3_BUCKET_NAME, Delete={'Objects': objects_to_delete})

        # Copy the new file into sidewalk-ota-src/current-firmware/
        copy_source = {'Bucket': OTA_S3_BUCKET_NAME, 'Key': file_name}
        destination_key = f'{current_firmware_prefix}{file_name}'
        s3.copy_object(CopySource=copy_source, Bucket=OTA_S3_BUCKET_NAME, Key=destination_key)

        return {
            'statusCode': 200,
            'body': json.dumps('File copied successfully')
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
