# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from typing import List

import boto3
import logging
import time

from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

from transfer import DeviceTransfer

logger = logging.getLogger(__name__)


class DeviceTransfersHandler:
    """
    A class that provides read and write methods for the DeviceTransfer table.
    """

    TABLE_NAME = 'DeviceTransfers'

    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    # ----------------
    # Read operations
    # ----------------

    def get_all_device_transfers(self) -> List[DeviceTransfer]:
        """
        Gets all available records from the DeviceTransfers table.

        :return:    List of DeviceTransfer objects.
        """
        try:
            response = self._table.scan()
            items = response.get('Items', [])

            for item in items:
                yield DeviceTransfer(**item)

            while "LastEvaluatedKey" in response:
                response = self._table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items = response.get('Items', [])

                for item in items:
                    yield DeviceTransfer(**item)

        except ClientError as err:
            logger.error(f'Error while calling get_all_device_transfers: {err}', exc_info=True)
            raise

    def get_device_transfer_details(self, device_id: str) -> DeviceTransfer:
        """
        Queries Measurements table for the records coming from given device withing a given time span.

        :param wireless_device_id:  Id of the wireless device.
        :return:                    List of DeviceTransfer objects.
        """
        items = []
        try:
            filter_expression = Attr('device_id').eq(device_id)
            response = self._table.scan(IndexName='device_id', FilterExpression=filter_expression)
            items.extend(response.get('Items', []))
            while "NextToken" in response:
                response = self._table.scan(IndexName='device_id',
                                            FilterExpression=filter_expression,
                                            NextToken=response["NextToken"])
                items.extend(response.get('Items', []))
        except ClientError as err:
            logger.error(f'Error while calling get_device_transfer: {err}')
            raise
        else:
            return DeviceTransfer(**items[0])

    # -----------------
    # Write operations
    # -----------------
    def add_device_transfer(self, deviceTransfer: DeviceTransfer):
        """
        Adds deviceTransfer object to the DeviceTransfers table.

        :param deviceId:  Device identifier.
        :return:             Updated DeviceTransfer object.
        """
        try:
            self._table.put_item(
                Item={
                    'device_id': deviceTransfer.get_device_id(),
                    'transfer_status': deviceTransfer.get_transfer_status(),
                    'firmware_version': deviceTransfer.get_firmware_version(),
                    'firmware_upgrade_status': deviceTransfer.get_firmware_upgrade_status(),
                    'transfer_start_time_UTC': deviceTransfer.get_transfer_start_time_UTC(),
                    'status_updated_time_UTC': deviceTransfer.get_status_updated_time_UTC(),
                    'transfer_end_time_UTC': deviceTransfer.get_transfer_end_time_UTC(),
                    'file_name': deviceTransfer.get_file_name(),
                    'file_size_kb': deviceTransfer.get_file_size_kb(),
                    'task_id': deviceTransfer.get_task_id()
                },
                ReturnValues="ALL_OLD"
            )
        except ClientError as err:
            logger.error(
                f'Error while calling add_device_transfer for wireless_device_id: {deviceTransfer.get_device_id()}: {err}'
            )
            raise
        else:
            return deviceTransfer

