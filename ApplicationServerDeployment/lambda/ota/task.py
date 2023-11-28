# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from decimal import Decimal
from typing import final, List


@final
class TransferTask(object):
    """
    A class that represents the TransferTask table record.
    """

    def __init__(self, task_id, task_status: str = None, creation_time_UTC: int = None, task_start_time_UTC: int = None, task_end_time_UTC: int = None,
                 file_name: str = None, file_size_kb: int = None, origination: str = None, device_ids: List[str] = None):
        self._task_id = task_id
        self._task_status = task_status
        self._creation_time_UTC = creation_time_UTC
        self._task_start_time_UTC = task_start_time_UTC
        self._task_end_time_UTC = task_end_time_UTC
        self._file_name = file_name
        self._file_size_kb = file_size_kb
        self._origination = origination
        self._device_ids = device_ids

    def get_task_id(self) -> str:
        return str(self._task_id)

    def get_task_status(self) -> str:
        return str(self._task_status)

    def get_creation_time_UTC(self) -> int:
        return int(self._creation_time_UTC)

    def get_task_start_time_UTC(self) -> int:
        return int(self._task_start_time_UTC)

    def get_task_end_time_UTC(self) -> int:
        return int(self._task_end_time_UTC)

    def get_file_name(self) -> str:
        return str(self._file_name)

    def get_file_size_kb(self) -> Decimal:
        return Decimal(self._file_size_kb)

    def get_origination(self) -> str:
        return str(self._origination)

    def get_device_ids(self) -> List[str]:
        return [str(device_id) for device_id in self._device_ids]


    def to_dict(self) -> dict:
        """
        Returns dict representation of the transfer task object.

        :return:    Dict representation of the TransferTask.
        """
        return {
            'task_id': self._task_id,
            'task_status': self._task_status,
            'creation_time_UTC': self._creation_time_UTC,
            'task_start_time_UTC': self._task_start_time_UTC,
            'task_end_time_UTC': self._task_end_time_UTC,
            'file_name': self._file_name,
            'file_size_kb': self._file_size_kb,
            'origination': self._origination,
            'device_ids': self._device_ids
        }
