# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles the request to delete the existing fuota task.
"""

import boto3
import json
import traceback

session = boto3.Session()
wireless_client = session.client(service_name='iotwireless', endpoint_url= 'https://api.gamma.us-east-1.iotwireless.iot.aws.dev')

def cancel_tasks(task_ids):
    print('Cancelling tasks: {task_ids}')
    error_response = []
    for task in task_ids: 
        try: 
            response = wireless_client.delete_fuota_task(
                Id=task
            )
            print(response)
        except Exception as e:
            error_response.append({'task': task, 'error': str(e)})
            print('task {task} error: %s',e)
    print('Unsuccessful list: {error_response}')
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

        if not error_response :
            return {
                    'statusCode': 200,
                }
        else :
            return {
                'statusCode': 500,
                'body': json.dumps(error_response)
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
