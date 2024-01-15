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
    print('Cancelling tasks: ', task_ids)
    error_response = []
    error_tasks = []
    for task in task_ids: 
        try: 
            response = iot_handler.delete_fuota_task(task)
            print(response)
        except Exception as e:
            error_tasks.append(task)
            error_response.append({'task': task, 'error': str(e)})
            print('task {task} error: %s',e)

    non_errored_tasks = [task_id for task_id in task_ids if task_id not in error_tasks]
    print('Non error task ', non_errored_tasks)
    # Update the database
    update_transfer_tasks_and_device_transfers(non_errored_tasks)
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
    device_task_map = []
    current_timestamp = int(datetime.utcnow().timestamp()*1000)
    # Update tasks
    for task_id in task_ids:
        print('Task Id to update ',task_id)
        task = transfer_tasks_handler.get_transfer_task_details(task_id=task_id)
        print('The db task: ', task.to_dict())
        task._task_status = 'CANCELLED'
        task._task_end_time_UTC = current_timestamp
        transfer_tasks_handler.update_transfer_task(task)
        for device_id in task._device_ids:
            device_task_map.append({'task_id': task_id, 'device_id': device_id})

    # Update device
    for map in device_task_map:
        device_id = map.get('device_id')
        task_id = map.get('task_id')
        device_response = device_transfers_handler.get_device_transfer_details_by_task(device_id=device_id, task_id=task_id)
        print('The db device: ', device_response.to_dict_camel_case())
        device_response._transfer_status = 'CANCELLED'
        device_response._firmware_upgrade_status = 'None'
        device_response._status_updated_time_UTC = current_timestamp
        device_response._transfer_end_time_UTC = current_timestamp
        print('The db device record to update: ', device_response.to_dict_camel_case())
        device_transfers_handler.update_device_transfer(device_response)


def parse_json_string(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")