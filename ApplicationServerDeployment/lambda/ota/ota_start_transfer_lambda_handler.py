# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

from datetime import datetime, timezone
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


class OTAStartTransferHandler:
    """
    A class that creates the transfer task
    """
    def __init__(self):
        self._device_transfers_handler = DeviceTransfersHandler()
        self._transfer_tasks_handler = TransferTasksHandler()
        self._iot_handler = IOTWirelessAPIHandler()
        # TODO - Replace with S3_Client
        self._s3 = boto3.client('s3')

    def create_task(self, file_name, start_time_utc, device_ids, fragment_size, is_device_trigger):

        # Mocked output values
        task_id = 'TaskId'
        task_status = 'PENDING'
        task_end_time_utc = None
        origination = 'DEVICE' if is_device_trigger else 'CLOUD'

        
        # Uncomment the code below for the actual implementation

        try:

            s3_bucket_name = os.environ.get('OTA_S3_BUCKET_NAME')
            fuota_s3_role_arn = os.environ.get('S3_FUOTA_ROLE_ARN')
            s3_uri = 's3://' + s3_bucket_name + '/' + file_name

            # Check if it the file is present in the s3 bucket & return the size of the file
            file_size = self.get_file_size(s3_bucket_name, file_name) if not is_device_trigger else self.get_current_file_size(s3_bucket_name, 'current-firmware/')
            print(f'file_size ', file_size)
            if file_size and file_size < 0:
                print('The file does not exists ',  file_name)
                raise FileNotFoundError(f"File not found!")
            file_size = file_size/1024  
            print(f'file_size in kb', file_size) 
            try :

                # Call the CreateFUOTATaskAPI
                create_fuota_task_response = self._iot_handler.create_fuota_task(s3_uri=s3_uri, s3_update_role=fuota_s3_role_arn, fragment_size=fragment_size)
                task_id = create_fuota_task_response.get('Id', '')
                print(f'task id ', task_id)
                print('task id ', create_fuota_task_response.get('Id', ''))

                # Call AssociateWirelessDeviceWithFuotaTask
                errored_devices = []
                
                for device in device_ids:
                    try: 
                        associate_wireless_devices_with_fuota_task = self._iot_handler.associate_wireless_device_with_fuota_task(
                            fuota_task_id=task_id,
                            wireless_device_id=device
                        )
                        print("Associate device to Fuota task response ", associate_wireless_devices_with_fuota_task)
                    except Exception as e:
                        print(f'Error in AssociateWirelessDeviceWithFuotaTask ', e)
                        errored_devices.append(device)

                # The start time for the transfer task for Sidewalk should always be atleast 5 minutes ahead of the current time
                utc_now = datetime.utcnow()
                print('utc_now ', utc_now)
                now_plus_6 = utc_now + timedelta(minutes=6)
                print('now_plus_6 ', now_plus_6)

                creation_time_utc_milliseconds = int(now_plus_6.timestamp() * 1000) if start_time_utc is None else start_time_utc
                print('Time taken into consideration for starting the FUOTA creation_time_utc: ', creation_time_utc_milliseconds)
                
                non_error_devices = [device_id for device_id in device_ids if device_id not in errored_devices]
                print("Non-error devices:", non_error_devices)
                print('utc to sailboat format ', self.utc_to_datetime(creation_time_utc_milliseconds))

                if non_error_devices:
                    # Call StartTransferTask API
                    start_fuota_task_response = iot_handler.start_fuota_task(
                        fuota_task_id=task_id,
                        start_time = self.utc_to_datetime(creation_time_utc_milliseconds)
                    )
                    print('Start FUOTA task API response, ', start_fuota_task_response)

                    # Add the entry to the tables
                    self.add_record_to_the_table(non_error_devices, task_id, int(creation_time_utc_milliseconds), file_name, file_size, origination)
                else:
                    print('Every device has error, skipping db save & start api call')
                return {
                        'taskId': task_id,
                        'taskStatus': task_status,
                        'creationTimeUTC': creation_time_utc_milliseconds,
                        'taskEndTimeUTC': task_end_time_utc,
                        'fileName': file_name,
                        'fileSizeKB': file_size,
                        'origination': origination,
                        'deviceIds': non_error_devices
                    }
            except Exception as e:
                print(f'Exception inner', e)
                raise e

        except Exception as e:
            print(f'Exception ', e)
            raise e
            


    def lambda_handler(self, event, context, is_device_trigger=False):
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
            file_name = ''
            if is_device_trigger:
                file_name=''
            else:
                file_name = json_body.get("fileName", "DefaultFileName")
            start_time_utc = json_body.get("startTimeUTC")
            device_ids = json_body.get("deviceIds", ["DefaultDeviceId"])
            fragment_size = json_body.get("fragmentSize", 1024)

            try:
                output = self.create_task(file_name, start_time_utc, device_ids, fragment_size, is_device_trigger)
                return {
                    'statusCode': 200,
                    'body': json.dumps(output)
                }
            except FileNotFoundError as fe:
                return {
                    'statusCode': 404,
                    'body': str(fe),
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': str(e),
                }
        except Exception:
            print(f'Unexpected error occurred: {traceback.format_exc()}')
            return {
                'statusCode': 500,
                'body': json.dumps('The task failed to create: ' + traceback.format_exc())
            }
        
    def check_file_exists(self, bucket_name, key):
        try:
            self._s3.head_object(Bucket=bucket_name, Key=key)
            return True
        except Exception as e:
            # If the file doesn't exist
            if e.response['Error']['Code'] == '404':
                return False
            print('Exception in checking the s3 file, {e}')
            return False

    def add_record_to_the_table(self, device_ids, task_id, start_time, file_name, file_size, origination):
        # Add all to the Transfer task table
        transfer_task = TransferTask(task_id=task_id, task_status='PENDING', creation_time_UTC=0, 
                                    file_name=file_name, file_size_kb=file_size, origination=origination,
                                    device_ids=device_ids, task_end_time_UTC=0, task_start_time_UTC=start_time)
        transfer_tasks_handler.add_transfer_task(transferTask = transfer_task)

        for device in device_ids:
            device_transfer = device_transfers_handler.get_device_transfer_details(device_id=device)
            device_transfer._transfer_status = 'PENDING'
            device_transfer._transfer_start_time_UTC = start_time
            device_transfer._file_name = file_name
            device_transfer._file_size_kb = file_size
            device_transfer._firmware_upgrade_status = 'PENDING'
            device_transfer._task_id=task_id
            device_transfers_handler.add_device_transfer(device_transfer)

    def get_file_size(self, bucket_name, key):
        try:
            response = self._s3.head_object(Bucket=bucket_name, Key=key)
            file_size = response['ContentLength']
            return file_size
        except Exception as e:
            # If the object doesn't exist, a specific exception is raised
            # If the file doesn't exist
            if e.response['Error']['Code'] == '404':
                return -1
            print('Exception in checking the s3 file, {e}')
            return -1
        
    def datetime_to_iot_format(self, dt):
        return dt.strftime("%Y%m%d%H%M%S")
    
    def datetime_to_int(self, dt):
        return dt.timestamp()
    
    def utc_to_datetime(self, utc_timestamp):
        utc_timestamp = utc_timestamp/1000
        dt = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=timezone.utc)
        formatted_datetime = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print('Formatted date and time ', formatted_datetime)
        return formatted_datetime
    
    def get_current_file_size(self, bucket_name, folder_path):
        # List objects in the folder
        try:
            response = self._s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
            if 'Contents' in response and len(response['Contents']) > 0:
                # Assuming there's only one file in the folder
                file_key = response['Contents'][1]['Key']
                file_size = response['Contents'][1]['Size']
                return file_size
        except Exception as e:
            print(f"Error fetching file size: {e}")
            return None

def lambda_handler(event, context):
    handler = OTAStartTransferHandler()
    return handler.lambda_handler(event, context, is_device_trigger=False)
