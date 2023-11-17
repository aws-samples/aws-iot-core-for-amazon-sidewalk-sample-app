# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles read request to SidewalkDevices and Measurements tables.
"""

import json
import traceback
import cors_utils
from typing import Final

from device_transfers_handler import DeviceTransfersHandler
from transfer_tasks_handler import TransferTasksHandler

device_transfers_handler: Final = DeviceTransfersHandler()
transfer_tasks_handler: Final = TransferTasksHandler()


def get_all_devices():
    """
    Get all records from the SidewalkDevices table.

    :return:    Response with list of records from SidewalkDevices table.
    """
    devices = device_transfers_handler.
    devices_json = []
    for device in devices:
        devices_json.append(device.to_dict())
    return _create_response_message(200, devices_json)


def lambda_handler(event, context):
    """
    Handles read request to SidewalkDevices and Measurements tables.
    """
    method = event.get("httpMethod")
    path = event.get("path").split("api", 1)[1]

    if "on.aws/" in path:
        path = path.split("on.aws", 1)[1]

    try:
        if path is not None and method is not None and method == "GET":  # get device request format devices/{deviceId}
            if path.startswith("/devices/"):
                split_path = path.split("/devices/", 1)
                if len(split_path) == 1:  # if no device id is specified we get all devices
                    return get_all_devices()

                wireless_device_id = split_path[1]
                device = device_handler.get_device(wireless_device_id)
                if device is None:
                    return _create_response_message(404, "No device found with id {}".format(wireless_device_id))
                return _create_response_message(200, device.to_dict())

            elif path == "/devices":
                return get_all_devices()

            elif path.startswith("/measurements/"):  # get device request format devices/{deviceId}
                # you can also optionally specify range: devices/{deviceId}/dateStart/dateEnd
                split_path = path.split("/measurements/", 1)
                if len(split_path) == 1:
                    return _create_response_message(400, "Invalid path. Device id needs to be specified. Example of correct "
                                                         "path /measurements/{wirelessDeviceId}")
                remaining_path = split_path[1].split("/", 1)
                wireless_device_id = remaining_path[0]

                measurements = measurement_handler.get_measurements_for_device(wireless_device_id=wireless_device_id)
                measurements_json = []
                for measurement in measurements:
                    measurements_json.append(measurement.to_dict())
                return _create_response_message(200, measurements_json)

            elif path == "/measurements":
                return _create_response_message(400, "Invalid path. Correct path format /measurements/{wirelessDeviceId}")
            else:
                return _create_response_message(400, "Invalid path. Endpoint {} is not supported".format(path))

        return _create_response_message(400, "Invalid path or method.")

    except Exception as e:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return _create_response_message(400, "Unexpected exception thrown {}".format(e))


def _create_response_message(status_code: int, body) -> dict:
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
    }
