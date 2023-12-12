# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from decimal import Decimal
from typing import final


@final
class DeviceTransfer(object):
    """
    A class that represents the DeviceTransfer table record.
    """

    def __init__(self, device_id, transfer_status: str = None, transfer_progress: int = None, status_updated_time_UTC: str = None, transfer_start_time_UTC: str = None,
                 transfer_end_time_UTC: str = None, file_name: str = None, file_size_kb: Decimal = None, firmware_upgrade_status: str = None,
                 firmware_version: str = None, task_id: str = None):
        self._device_id = device_id
        self._transfer_status = transfer_status
        self._transfer_progress = transfer_progress
        self._status_updated_time_UTC = status_updated_time_UTC
        self._transfer_start_time_UTC = transfer_start_time_UTC
        self._transfer_end_time_UTC = transfer_end_time_UTC
        self._file_name = file_name
        self._file_size_kb = file_size_kb
        self._firmware_upgrade_status = firmware_upgrade_status
        self._firmware_version = firmware_version
        self._task_id = task_id

    def get_device_id(self) -> str:
        return self._device_id

    def get_transfer_status(self) -> str:
        return self._transfer_status

    def get_transfer_progress(self) -> int:
        return int(self._transfer_progress)

    def get_status_updated_time_UTC(self) -> str:
        return self._status_updated_time_UTC

    def get_transfer_start_time_UTC(self) -> str:
        return self._transfer_start_time_UTC

    def get_transfer_end_time_UTC(self) -> str:
        return self._transfer_end_time_UTC

    def get_file_name(self) -> str:
        return self._file_name

    def get_file_size_kb(self) -> Decimal:
        return Decimal(self._file_size_kb)

    def get_firmware_upgrade_status(self) -> str:
        return self._firmware_upgrade_status

    def get_firmware_version(self) -> str:
        return self._firmware_version

    def get_task_id(self) -> str:
        return self._task_id

    def to_dict(self) -> dict:
        """
        Returns dict representation of the DeviceTransfer object.

        :return:    Dict representation of the DeviceTransfer.
        """
        return {
            'device_id': self._device_id,
            'task_id': self._task_id,
            'transfer_status': self._transfer_status,
            'transfer_progress': self._transfer_progress,
            'status_updated_time_UTC': self._status_updated_time_UTC,
            'transfer_start_time_UTC': self._transfer_start_time_UTC,
            'transfer_end_time_UTC': self._transfer_end_time_UTC,
            'file_name': self._file_name,
            'file_size_kb': self._file_size_kb,
            'firmware_upgrade_status': self._firmware_upgrade_status,
            'firmware_version': self._firmware_version
        }
