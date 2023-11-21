# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles read request to SidewalkDevices and Measurements tables.
"""

import json
import traceback
import cors_utils
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
    device_transfers_json = []
    for device_transfer in device_transfers:
        device_transfers_json.append(device_transfer.to_dict())
    print(device_transfers_json)
    return _create_response_message(200, device_transfers_json)

def get_all_transfer_tasks():
    """
    Get all records from the TransferTasks table.

    :return:    Response with list of records from TransferTasks table.
    """
    transfer_tasks = transfer_tasks_handler.get_all_transfer_tasks()
    transfer_tasks_json = []
    for transfer_task in transfer_tasks:
        transfer_tasks_json.append(transfer_task.to_dict())
    print(transfer_tasks_json)
    return _create_response_message(200, transfer_tasks_json)


def lambda_handler(event, context):
    """
    Handles read request to DeviceTransfers and TransferTasks tables.
    """
    method = event.get("httpMethod")
    path = event.get("path").split("api", 1)[1]

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
                    return get_all_device_transfers()

                wireless_device_id = split_path[1]
                print(f'DeviceId is:' + wireless_device_id)
                device = device_transfers_handler.get_device_transfer_details(wireless_device_id)
                if device is None:
                    return _create_response_message(404, "No device found with id {}".format(wireless_device_id))
                return _create_response_message(200, device.to_dict())

            elif path == "/ota/deviceTransfers":
                return get_all_device_transfers()

            elif path.startswith("/ota/transferTasks/"):
                split_path = path.split("/ota/transferTasks/", 1)
                print(f'Path is: {split_path[1]}')
                if len(split_path) < 1:
                    print('len not 1')
                    return get_all_transfer_tasks()

                task_id = split_path[1]
                print('task Id' + task_id)
                task = transfer_tasks_handler.get_transfer_task_details(task_id)
                if task is None:
                    return _create_response_message(404, "No transfer found with id {}".format(task_id))
                return _create_response_message(200, task.to_dict())

            elif path == "/ota/transferTasks":
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
