# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles the request to delete the existing fuota task.
"""

from datetime import datetime
from typing import Final
import json
import traceback

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

from ota_wireless_api_handler import IOTWirelessAPIHandler


device_transfers_handler: Final = DeviceTransfersHandler()
iot_handler: Final = IOTWirelessAPIHandler()
transfer_tasks_handler: Final = TransferTasksHandler()

def cancel_tasks(task_ids):
    print('Cancelling tasks: {task_ids}')
    error_response = []
    # for task in task_ids: 
    #     try: 
    #         response = iot_handler.delete_fuota_task(task)
    #         print(response)
    #     except Exception as e:
    #         error_response.append({'task': task, 'error': str(e)})
    #         print('task {task} error: %s',e)

    # # Update the database
    # update_transfer_tasks_and_device_transfers(task_ids)
    return error_response


def lambda_handler(event, context):
    """
    Handler to delete the existing fuota task.
    """
    try:
        # ---------------------------------------------------------------
        # Receive the request
        # Extract the tasks to delete/cancel
        # ---------------------------------------------------------------
        print(f'Received event: {event}')

        # Extract input values from the API Gateway request
        body = parse_json_string(event.get('body', {}))
        task_ids = body.get("taskIds", [])
        error_response = cancel_tasks(task_ids)

        if error_response :
            return {
                'statusCode': 500,
                'body': json.dumps(error_response)
            }
        else :
            return {
                'statusCode': 200,
            }
    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
    

def update_transfer_tasks_and_device_transfers(task_ids):
    device_ids = []
    current_timestamp = int(datetime.utcnow().timestamp())
    # Update tasks
    for task_id in task_ids:
        task = transfer_tasks_handler.get_transfer_task_details(taskId=task_id)
        task._task_status = 'Canceled'
        task._task_end_time_UTC = current_timestamp
        transfer_tasks_handler.update_transfer_task(task)
        for device_id in task._device_ids:
            device_ids.append(device_id)

    # Update device
    for device_id in device_ids:
        device_response = device_transfers_handler.get_device_transfer_details(deviceId=device_id)
        device_response._transfer_status = 'Canceled'
        device_response._firmware_upgrade_status = 'None'
        device_response._status_updated_time_UTC = current_timestamp
        device_response.get_transfer_end_time_UTC = current_timestamp
        device_transfers_handler.update_device_transfer(device_response)


def parse_json_string(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")