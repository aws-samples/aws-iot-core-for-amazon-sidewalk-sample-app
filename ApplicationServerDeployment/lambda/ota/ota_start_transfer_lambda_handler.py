# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

from datetime import datetime, timezone, time
from random import random
from typing import Final

import boto3
import json
import traceback

from command import Command
from device import Device
from command import Command
from device import Device

import time_utils
from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()


def create_task(file_name, start_time_utc, device_ids):
    if start_time_utc < int(time.time()):
        return {
            'statusCode': 400,
            'body': json.dumps('The startTime is invalid'),
        }

    if any(device_id not in ['DeviceId1', 'DeviceId2'] for device_id in device_ids):
        return {
            'statusCode': 404,
            'body': json.dumps('One or more deviceIds do not exist'),
        }

    if any(device_id in ['PendingDeviceId', 'InProgressDeviceId'] for device_id in device_ids):
        return {
            'statusCode': 409,
            'body': json.dumps('One or more deviceIds is already Pending or Transferring'),
        }

        # Mocked output values
        task_id = 'TaskId'
        task_status = 'COMPLETED'
        creation_time_utc = int(time.time())
        task_end_time_utc = None
        file_size_kb = random.randint(1, 1024)
        origination = 'App'

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
        # Decode payload data.
        # ---------------------------------------------------------------
        print(f'Received event: {event}')

        # Extract input values from the API Gateway request
        file_name = event.get('body', {}).get('fileName', 'DefaultFileName')
        start_time_utc = event.get('body', {}).get('startTimeUTC', int(time.time()))
        device_ids = event.get('body', {}).get('deviceIds', ['DefaultDeviceId'])

        try:
            output = create_task(file_name, start_time_utc, device_ids)
            return {
                'statusCode': 200,
                'body': json.dumps(output)
            }
        except Exception:
            return {
                'statusCode': 500,
                'body': json.dumps('Unexpected error {}.'),
            }
    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('The task failed to create: ' + traceback.format_exc())
        }
