# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles read request to SidewalkDevices and Measurements tables.
"""

import json
import traceback
from typing import Final
from decimal import Decimal

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()


def get_all_device_transfers():
    """
    Get all records from the DeviceTransfers table.

    :return:    Response with list of records from DeviceTransfers table.
    """
    device_transfers = device_transfers_handler.get_all_device_transfers()
    device_transfers_json = {"wireless_devices": []}
    for device_transfer in device_transfers:
        device_transfers_json["wireless_devices"].append(device_transfer.to_dict())
    print(device_transfers_json)
    return _create_response_message(200, device_transfers_json)

def get_all_transfer_tasks():
    """
    Get all records from the TransferTasks table.

    :return:    Response with list of records from TransferTasks table.
    """
    transfer_tasks = transfer_tasks_handler.get_all_transfer_tasks()
    transfer_tasks_json = {"transfer_tasks": []}
    for transfer_task in transfer_tasks:
        transfer_tasks_json["transfer_tasks"].append(transfer_task.to_dict())
    print(transfer_tasks_json)
    return _create_response_message(200, transfer_tasks_json)


def mock_transfers_tasks():
    transfer_tasks_mock_json = {
        "transfer_tasks": [
            {
                "task_id": "TaskId1",
                "task_status": "enum",
                "creation_time_UTC": 1234567890,
                "task_start_time_UTC": 1234567890,
                "task_end_time_UTC": 1234567890,
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "origination": "CLOUD",
                "device_ids": [
                    "DeviceId1","DeviceId2","DeviceId3"
                ]
            },
            {
                "task_id": "TaskId2",
                "task_status": "enum",
                "creation_time_UTC": 1234567890,
                "task_start_time_UTC": 1234567890,
                "task_end_time_UTC": 1234567890,
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "origination": "CLOUD",
                "device_ids": [
                    "DeviceId4","DeviceId5","DeviceId6"
                ]
            },
            {
                "task_id": "TaskId3",
                "task_status": "enum",
                "creation_time_UTC": 1234567890,
                "task_start_time_UTC": 1234567890,
                "task_end_time_UTC": 1234567890,
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "origination": "CLOUD",
                "device_ids": [
                    "DeviceId7","DeviceId8","DeviceId9"
                ]
            }
        ]
    }

    return _create_response_message(200, transfer_tasks_mock_json)

def mock_device_transfers():
    wireless_devices_mock_json = {
        "wireless_devices": [
            {
                "device_id": "DeviceId1",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 50,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId1"
            },
            {
                "device_id": "DeviceId2",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 30,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId1"
            },
            {
                "device_id": "DeviceId3",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 80,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId1"
            },
            {
                "device_id": "DeviceId4",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 90,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId2"
            },
            {
                "device_id": "DeviceId5",
                "transfer_status": "COMPLETE",  # Replace "enum" with an actual transfer status value
                "progress_pct": 100,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId2"
            },
            {
                "device_id": "DeviceId6",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 50,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId2"
            },
            {
                "device_id": "DeviceId7",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 10,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "3",
                "task_id": "TaskId1"
            },
            {
                "device_id": "DeviceId8",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 20,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "3"
            },
            {
                "device_id": "DeviceId9",
                "transfer_status": "PENDING",  # Replace "enum" with an actual transfer status value
                "progress_pct": 24,
                "status_updated_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_start_time_UTC": 1234567890,  # Replace with an actual timestamp
                "transfer_end_time_UTC": 1234567890,  # Replace with an actual timestamp
                "file_name": "abcd.txt",
                "file_size_kb": 1024,  # Replace with an actual file size in kilobytes
                "firmware_upgrade_status": "PENDING",  # Replace "enum" with an actual firmware upgrade status value
                "firmware_version": "5",
                "task_id": "TaskId3"
            }
        ]
    }

    return _create_response_message(200, wireless_devices_mock_json)

def lambda_handler(event, context):
    """
    Handles read request to DeviceTransfers and TransferTasks tables.
    """
    method = event.get("httpMethod")
    path = event.get("path").split("api", 1)[1]
    mock = False

    if "on.aws/" in path:
        path = path.split("on.aws", 1)[1]
        print(f'Path is:' + path)

    try:
        if path is not None and method is not None and method == "GET":  # get device request format deviceTransfers/{deviceId}
            if path.startswith("/ota/deviceTransfers/"):
                split_path = path.split("/ota/deviceTransfers/", 1)
                print(f'Path is: {split_path[1]}')
                if len(split_path) < 1:  # if no device id is specified we get all device transfers
                    print('len not 1')
                    if mock:
                        return mock_device_transfers()
                    else:
                        return get_all_device_transfers()

                wireless_device_id = split_path[1]
                print(f'DeviceId is:' + wireless_device_id)
                device = device_transfers_handler.get_device_transfer_details(wireless_device_id)
                if device is None:
                    return _create_response_message(404, "No device found with id {}".format(wireless_device_id))
                return _create_response_message(200, device.to_dict())

            elif path == "/ota/deviceTransfers":
                if mock:
                    return mock_device_transfers()
                else:
                    return get_all_device_transfers()

            elif path.startswith("/ota/transferTasks/"):
                split_path = path.split("/ota/transferTasks/", 1)
                print(f'Path is: {split_path[1]}')
                if len(split_path) < 1:
                    print('len not 1')
                    if mock:
                        return mock_transfers_tasks()
                    else:
                        return get_all_device_transfers()

                task_id = split_path[1]
                print('task Id' + task_id)
                task = transfer_tasks_handler.get_transfer_task_details(task_id)
                if task is None:
                    return _create_response_message(404, "No transfer found with id {}".format(task_id))
                return _create_response_message(200, task.to_dict())

            elif path == "/ota/transferTasks":
                if mock:
                    return mock_transfers_tasks()
                else:
                    return get_all_transfer_tasks()

        return _create_response_message(400, "Invalid path or method.")

    except Exception as e:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return _create_response_message(400, "Unexpected exception thrown {}".format(e))


def _create_response_message(status_code: int, body) -> dict:
    return {
        'statusCode': status_code,
        'body': json.dumps(body, default=_json_encoder),
    }

def _json_encoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type {} is not JSON serializable".format(type(obj)))
