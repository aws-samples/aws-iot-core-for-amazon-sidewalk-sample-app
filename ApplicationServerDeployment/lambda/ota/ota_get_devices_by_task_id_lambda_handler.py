# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles equest to get the list of devices associated with Fuota task
"""

import json
import traceback


def lambda_handler(event, context):
    """
    Handles request to get the list of devices associated with Fuota task
    """
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Fetch the wireless devices associated with the given fuota task
        # ---------------------------------------------------------------
        print(f'Received event: {event}')

        # Extract input values from the API Gateway request
        query_params = event.get('queryStringParameters', {})
        fuota_task_id = query_params.get('fuotaTaskId', '')
        
        # call the Sailboat API

        deviceList = []
        deviceList.append({'status':"PENDING", 'deviceId' : 'device_id_1'})
        deviceList.append({'status':"PENDING", 'deviceId' : 'device_id_2'})

        return {
            'statusCode': 200,
            'body': json.dumps({'deviceList': deviceList})
        }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
