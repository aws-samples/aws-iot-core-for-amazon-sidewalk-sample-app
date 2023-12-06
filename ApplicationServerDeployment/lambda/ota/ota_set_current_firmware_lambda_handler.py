# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles setting current firmware file.
"""
import os
import json
import traceback
import boto3
from typing import Final
from botocore.exceptions import ClientError

OTA_S3_BUCKET_NAME: Final = os.environ.get('OTA_S3_BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Retrieve fileName from the request body
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

        file_name_with_ext = json_body.get("filename")

        # Ensure the fileName is provided
        if not file_name_with_ext:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request: fileName is required')
            }

        s3 = boto3.client('s3')

        # Delete all files in sidewalk-ota-src/current-firmware/
        current_firmware_prefix = 'current-firmware/'
        current_firmware_objects = s3.list_objects_v2(Bucket=OTA_S3_BUCKET_NAME, Prefix=current_firmware_prefix)

        if 'Contents' in current_firmware_objects and current_firmware_objects['Contents']:

            objects_to_delete = [{'Key': obj['Key']} for obj in current_firmware_objects['Contents'] if obj['Key'].startswith(current_firmware_prefix)]

            if objects_to_delete:
                s3.delete_objects(Bucket=OTA_S3_BUCKET_NAME, Delete={'Objects': objects_to_delete})
            else:
                print("No objects found within the 'current-firmware/' prefix.")
        else:
            print("No objects found with the specified prefix.")

        # Copy the new file into sidewalk-ota-src/current-firmware/
        source_bucket = OTA_S3_BUCKET_NAME
        source_key = file_name_with_ext
        destination_key = f'{current_firmware_prefix}{file_name_with_ext}'
        try:
            s3.head_object(Bucket=source_bucket, Key=source_key)
            statusCode = 200
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                response_message = {'body': json.dumps({'error': f"The source object '{source_key}' in bucket '{source_bucket}' does not exist."})}
                statusCode = 404
            else:
                response_message = {'body': json.dumps({'error': f"Unexpected error occurred: {traceback.format_exc()}"})}
                statusCode = 500
        else:
            s3.copy_object(CopySource={'Bucket': source_bucket, 'Key': source_key}, Bucket=OTA_S3_BUCKET_NAME, Key=destination_key)
            response_message = {'body': json.dumps({'success': f"Object '{source_key}' copied successfully."})}


        return {
            'statusCode': statusCode,
            'body': json.dumps(response_message)
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
