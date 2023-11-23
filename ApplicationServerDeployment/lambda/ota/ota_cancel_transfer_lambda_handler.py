# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles the request to delete the existing fuota task.
"""

from typing import Final
import json
import traceback

from ota_wireless_api_handler import IOTWirelessAPIHandler

iot_handler: Final = IOTWirelessAPIHandler()

def cancel_tasks(task_ids):
    print('Cancelling tasks: {task_ids}')
    error_response = []
    for task in task_ids: 
        try: 
            response = iot_handler.delete_fuota_task(task)
            print(response)
        except Exception as e:
            error_response.append({'task': task, 'error': str(e)})
            print('task {task} error: %s',e)
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
    
def parse_json_string(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")