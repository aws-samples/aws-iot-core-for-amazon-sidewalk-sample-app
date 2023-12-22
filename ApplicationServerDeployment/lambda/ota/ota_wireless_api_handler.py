# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import datetime
import boto3
import logging

logger = logging.getLogger(__name__)


class IOTWirelessAPIHandler:
    """
    A class that has all the API calls for wireless API's
    """

    def __init__(self):
        self._session = boto3.Session()
        self._wireless_client = self._session.client(service_name='iotwireless')

    def delete_fuota_task(self, fuota_task_id: str):
        return self._wireless_client.delete_fuota_task(
            Id=fuota_task_id
        )

    def list_wireless_devices(self, fuota_task_id='', max_results=20, next_token=''):
        return self._wireless_client.list_wireless_devices(
            FuotaTaskId=fuota_task_id,
            MaxResults=max_results,
            NextToken=next_token
        )
    
    def list_fuota_tasks(self, max_results=20, next_token=''):
        return self._wireless_client.list_fuota_tasks(
            MaxResults=max_results,
            NextToken=next_token
        )

    def create_fuota_task(self, s3_uri: str, s3_update_role: str, file_size: int):
        return self._wireless_client.create_fuota_task(
            FirmwareUpdateImage=s3_uri,
            FirmwareUpdateRole=s3_update_role,
            ProtocolType='Sidewalk',
            FragmentSizeBytes=file_size
        )
    
    def associate_wireless_device_with_fuota_task(self, fuota_task_id: str, wireless_device_id: str):
        return self._wireless_client.associate_wireless_device_with_fuota_task(
            Id=fuota_task_id,
            WirelessDeviceId=wireless_device_id
        )
    
    def start_fuota_task(self, fuota_task_id: str, start_time: datetime):
        return self._wireless_client.start_fuota_task(
            Id=fuota_task_id,
            Sidewalk={
                'StartTime': start_time
            }
        )
    
    def get_fuota_task(self, task_id: str):
        return self._wireless_client.get_fuota_task(Id=task_id)