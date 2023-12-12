# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

import base64
import boto3
import json
import traceback
from datetime import datetime, timezone
from typing import Final
import logging
from device_transfers_handler import DeviceTransfersHandler
from ota_wireless_api_handler import IOTWirelessAPIHandler
from transfer_tasks_handler import TransferTasksHandler
from transfer import DeviceTransfer
from task import TransferTask

SOME_CONSTANT: Final = "SOME_CONSTANT"

logger = logging.getLogger(__name__)

class OTANotificationsHandler:
    """
    A class that stores notifications in DB
    """
    def __init__(self):
        self._device_transfers_handler = DeviceTransfersHandler()
        self._transfer_tasks_handler = TransferTasksHandler()
        self._iot_handler = IOTWirelessAPIHandler()

    def update_device_firmware_upgrade_status(self, wireless_device_id: str, firmware_upgrade_status: str):
        device_transfer = DeviceTransfer(
            device_id=wireless_device_id,
            firmware_upgrade_status=firmware_upgrade_status
        )
        return self._device_transfers_handler.update_device_transfer_firmware_upgrade_status(device_transfer)
    def update_device_firmware_version(self, wireless_device_id: str, firmware_version: str):
        device_transfer = DeviceTransfer(
            device_id=wireless_device_id,
            firmware_version=firmware_version
        )
        return self._device_transfers_handler.update_device_transfer_firmware_version(device_transfer)

    def update_device_progress_pct(self, wireless_device_id: str, progress_pct: str):
        device_transfer = DeviceTransfer(
            device_id=wireless_device_id,
            transfer_progress=int(progress_pct)
        )
        return self._device_transfers_handler.update_device_transfer_progress_pct(device_transfer)

    def update_transfer_start_details(self, wireless_device_id: str, fuota_task_id: str, timestamp: int, status: str):
        if status == "Successful":
            status = "PENDING"
        device_transfer = DeviceTransfer(
            device_id=wireless_device_id,
            task_id=fuota_task_id,
            transfer_start_time_UTC=str(timestamp),
            status_updated_time_UTC=str(timestamp),
            transfer_status=status
        )
        self.update_transfer_task_status(fuota_task_id)
        return self._device_transfers_handler.update_device_transfer_start_details(device_transfer)

    def update_transfer_finish_details(self, wireless_device_id: str, fuota_task_id: str, timestamp: int, status: str):
        if status == "Successful":
            status = "COMPLETE"
        # TODO - Canceled and Failed
        device_transfer = DeviceTransfer(
            device_id=wireless_device_id,
            task_id=fuota_task_id,
            transfer_end_time_UTC=str(timestamp),
            status_updated_time_UTC=str(timestamp),
            transfer_status=status
        )
        self.update_transfer_task_status(fuota_task_id)
        return self._device_transfers_handler.update_device_transfer_finish_details(device_transfer)

    def update_transfer_task_status(self, task_id):
        # Call the sailboat API
        task_response = self._iot_handler.get_fuota_task(task_id=task_id)
        print('IOT getFuotaTask response ', task_response)
        task = self._transfer_tasks_handler.get_transfer_task_details(task_id=task_id)
        task._task_status = task_response.get('Status')
        self._transfer_tasks_handler.update_transfer_task(transfer_task=task)
        print('Updated the task ', task)
        
    def save_fuota_task_notifications(self, payload):
        if payload is not None:
            try:
                #payload = json.loads(notification)
                event_type = payload.get("eventType")
                device_id = payload.get("WirelessDeviceId")
                task_id = payload.get("FuotaTaskId")
                timestamp = payload.get("timestamp")
                Sidewalk = payload.get("Sidewalk")

                if event_type and task_id and timestamp and Sidewalk:
                    transfer_status = Sidewalk.get("Status")

                # Perform additional processing or validation as needed
                # ...

                if event_type == "started":
                    self.update_transfer_start_details(device_id, task_id, timestamp, transfer_status)

                elif event_type == "finished":
                    self.update_transfer_finish_details(device_id, task_id, timestamp, transfer_status)

                else:
                    return {
                        'statusCode': 400,
                        'body': json.dumps('Invalid eventType value.')
                    }
                return {
                    'statusCode': 200,
                    'body': json.dumps('Notification received')
                }
            except json.JSONDecodeError as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Invalid JSON format in the notification field.')
                }

