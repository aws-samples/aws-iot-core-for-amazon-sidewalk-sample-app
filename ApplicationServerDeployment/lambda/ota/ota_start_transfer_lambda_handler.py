# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

from datetime import datetime, timezone, time
import os
from random import random
from typing import Final

import boto3
import json
import traceback

from datetime import datetime, timedelta
from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler
from transfer import DeviceTransfer
from ota_wireless_api_handler import IOTWirelessAPIHandler
from task import TransferTask

device_transfers_handler: Final = DeviceTransfersHandler()
iot_handler: Final = IOTWirelessAPIHandler()
transfer_tasks_handler: Final = TransferTasksHandler()


s3 = boto3.client('s3')
# TODO - Replace with S3_Client

def create_task(file_name, start_time_utc, device_ids):

    # Mocked output values
    task_id = 'TaskId'
    task_status = 'PENDING'
    creation_time_utc = start_time_utc
    task_end_time_utc = None
    file_size_kb = 1024
    origination = 'App'

    
    # Uncomment the code below for the actual implementation

    # try:

    #     s3_bucket_name = os.environ.get('OTA_S3_BUCKET_NAME')
    #     fuota_s3_role_arn = os.environ.get('S3_FUOTA_ROLE_ARN')
    #     s3_uri = 's3://' + s3_bucket_name + '/' + file_name

    #     # Check if it the file is present in the s3 bucket & return the size of the file
    #     file_size = get_file_size(s3_bucket_name, file_name)
    #     print(f'file_size ', file_size)
    #     if file_size < 0:
    #         print('The file does not exists ',  file_name)
    #         return
        
    #     if file_size < 1024:
    #         print('The file less than 1024 ',  file_name)
    #         file_size = 1024
            
    #     # Call the CreateFUOTATaskAPI
    #     create_fuota_task_response = iot_handler.create_fuota_task(s3_uri=s3_uri, s3_update_role=fuota_s3_role_arn, file_size=file_size)
    #     task_id = create_fuota_task_response.get('Id', '')
    #     print(f'task id ', task_id)

    #     # Call AssociateWirelessDeviceWithFuotaTask
    #     errored_devices = []
        
    #     for device in device_ids:
    #         try: 
    #             associate_wireless_devices_with_fuota_task = iot_handler.associate_wireless_device_with_fuota_task(
    #                 fuota_task_id=task_id,
    #                 wireless_device_id=device
    #             )
    #         except e:
    #             print(f'Error in AssociateWirelessDeviceWithFuotaTask ', e)
    #             errored_devices.append(device)

    #     # The start time for the transfer task for Sidewalk should always be 5 minutes ahead of the current time
        # now = datetime.now()
        # now_plus_5 = now + timedelta(minutes=5)
    #     # Call StartTransferTask API
    #     iot_handler.start_fuota_task(
    #         fuota_task_id=task_id,
    #         start_time = now_plus_5
    #     )

    #     # Add the entry to the tables
    #     add_record_to_the_table(device_ids, task_id, now, file_name, file_size)

    # except Exception as e:
    #     print(f'Exception ', e)

    return {
        'taskId': task_id,
        'taskStatus': task_status,
        'creationTimeUTC': creation_time_utc,
        'taskEndTimeUTC': task_end_time_utc,
        'fileName': file_name,
        'fileSizeKB': file_size_kb,
        'origination': origination,
        'deviceIds': device_ids
    }


def lambda_handler(event, context):
    """
    Handles events triggered by incoming ota actions.
    """
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Read its metadata.
        # Validates & fetches s3 object & creates the Fuota task.
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

        # Extract input values from the API Gateway request
        file_name = json_body.get("fileName", "DefaultFileName")
        start_time_utc = json_body.get("startTimeUTC", 123456789)
        device_ids = json_body.get("deviceIds", ["DefaultDeviceId"])

        try:
            output = create_task(file_name, start_time_utc, device_ids)
            return {
                'statusCode': 200,
                'body': json.dumps(output)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Unexpected error: {str(e)}'),
            }
    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('The task failed to create: ' + traceback.format_exc())
        }
    
def check_file_exists(bucket_name, key):
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return True
    except Exception as e:
        # If the file doesn't exist
        if e.response['Error']['Code'] == '404':
            return False
        print('Exception in checking the s3 file, {e}')
        return False

def add_record_to_the_table(device_ids, task_id, start_time, file_name, file_size):
    # Add all to the Transfer task table
    transfer_task = TransferTask(task_id=task_id, task_status='PENDING', creation_time_UTC=datetime_to_int(start_time), 
                                 file_name=file_name, file_size_kb=file_size, origination='CLOUD',
                                 device_ids=device_ids, task_end_time_UTC=0, task_start_time_UTC=0)
    transfer_tasks_handler.add_transfer_task(transferTask = transfer_task)

    for device in device_ids:
        device_transfer = DeviceTransfer(device_id=device, transfer_status='PENDING', 
                                         status_updated_time_UTC=0, transfer_start_time_UTC=0, 
                                         transfer_end_time_UTC=0, file_name=file_name, 
                                         file_size_kb=file_size, firmware_upgrade_status='PENDING', 
                                         firmware_version=0, task_id=task_id)
        device_transfers_handler.add_device_transfer(device_transfer)
    
    # Add all to Device Transfers table
    print()

def get_file_size(bucket_name, key):
    try:
        response = s3.head_object(Bucket=bucket_name, Key=key)
        file_size = response['ContentLength']
        return file_size
    except Exception as e:
        # If the object doesn't exist, a specific exception is raised
        # If the file doesn't exist
        if e.response['Error']['Code'] == '404':
            return -1
        print('Exception in checking the s3 file, {e}')
        return -1
    
def datetime_to_int(dt):
    return int(dt.strftime("%Y%m%d%H%M%S"))
