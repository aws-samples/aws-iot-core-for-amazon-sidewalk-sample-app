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

from device import Device
from device import Device

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()


def create_task(file_name, start_time_utc, device_ids):

    # Mocked output values
    task_id = 'TaskId'
    task_status = 'COMPLETED'
    creation_time_utc = start_time_utc
    task_end_time_utc = None
    file_size_kb = 1024
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
        start_time_utc = event.get('body', {}).get('startTimeUTC', 123456789)
        device_ids = event.get('body', {}).get('deviceIds', ['DefaultDeviceId'])

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
