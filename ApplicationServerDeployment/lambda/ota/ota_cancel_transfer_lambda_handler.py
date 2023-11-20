# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

import json
import traceback
from typing import Final


SOME_CONSTANT: Final = "SOME_CONSTANT"

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()

def cancel_tasks(task_ids):
    print(f'Cancelling tasks: {task_ids}')
    # Update db


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
        task_ids = event.get('body', {}).get('taskIds', [])

        cancel_tasks(task_ids)

        return {
            'statusCode': 200,
            'body': json.dumps('Tasks canceled successfully')
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
