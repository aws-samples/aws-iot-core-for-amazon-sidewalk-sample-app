# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
import logging

from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key

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

    def get_all_device_transfers(self) -> [DeviceTransfer]:
        """
        Gets all available records from the DeviceTransfers table.

        :return:    List of DeviceTransfer objects.
        """
        items = []
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
            response = self._table.query(KeyConditionExpression=Key('device_id').eq(device_id))
            items = response.get('Items', [])
        except ClientError as err:
            logger.error(f'Error while calling get_device_transfer_details: {err}')
            raise
        else:
            return DeviceTransfer(**items[0])

    # -----------------
    # Write operations
    # -----------------
    def add_device_transfer(self, device_transfer: DeviceTransfer):
        """
        Adds deviceTransfer object to the DeviceTransfers table.

        param device_transfer:  Device identifier.
        :return:               Updated DeviceTransfer object.
        """
        try:
            self._table.put_item(
                Item={
                    'device_id': device_transfer.get_device_id(),
                    'transfer_status': device_transfer.get_transfer_status(),
                    'firmware_version': device_transfer.get_firmware_version(),
                    'firmware_upgrade_status': device_transfer.get_firmware_upgrade_status(),
                    'transfer_start_time_UTC': device_transfer.get_transfer_start_time_UTC(),
                    'status_updated_time_UTC': device_transfer.get_status_updated_time_UTC(),
                    'transfer_end_time_UTC': device_transfer.get_transfer_end_time_UTC(),
                    'file_name': device_transfer.get_file_name(),
                    'file_size_kb': device_transfer.get_file_size_kb(),
                    'task_id': device_transfer.get_task_id()
                },
                ReturnValues="ALL_OLD"
            )
        except ClientError as err:
            logger.error(
                f'Error while calling add_device_transfer for wireless_device_id: {device_transfer.get_device_id()}: {err}'
            )
            raise
        else:
            return device_transfer

    def update_device_transfer_start_details(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object in the DeviceTransfers table.

        param deviceTransfer: Updated DeviceTransfer object.
        """
        try:
            self._table.update_item(
                Key={
                    'device_id': device_transfer.get_device_id(),
                    'task_id': device_transfer.get_task_id()
                },
                UpdateExpression="SET transfer_status = :status, "
                                 "transfer_start_time_UTC = :start_time, "
                                 "status_updated_time_UTC = :status_time ",
                ExpressionAttributeValues={
                    ':status': device_transfer.get_transfer_status(),
                    ':start_time': device_transfer.get_transfer_start_time_UTC(),
                    ':status_time': device_transfer.get_status_updated_time_UTC()
                },
                ReturnValues="ALL_NEW"  # You can adjust the return values as needed
            )
        except Exception as e:
            # Handle the exception according to your requirements
            print(f"Error updating item: {e}")

    def update_device_transfer_fimware_upgrade_status(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object in the DeviceTransfers table.

        param deviceTransfer: Updated DeviceTransfer object.
        """
        try:
            self._table.update_item(
                Key={
                    'device_id': device_transfer.get_device_id(),
                    'task_id': device_transfer.get_task_id()
                },
                UpdateExpression="SET firmware_upgrade_status = :upgrade_status, "
                                 "status_updated_time_UTC = :status_time ",
                ExpressionAttributeValues={
                    ':upgrade_status': device_transfer.get_firmware_upgrade_status(),
                    ':status_time': device_transfer.get_status_updated_time_UTC()
                },
                ReturnValues="ALL_NEW"  # You can adjust the return values as needed
            )
        except Exception as e:
            # Handle the exception according to your requirements
            print(f"Error updating item: {e}")

    def update_device_transfer_finish_details(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object in the DeviceTransfers table.

        param deviceTransfer: Updated DeviceTransfer object.
        """
        try:
            self._table.update_item(
                Key={
                    'device_id': device_transfer.get_device_id(),
                    'task_id': device_transfer.get_task_id()
                },
                UpdateExpression="SET transfer_status = :status, "
                                 "firmware_upgrade_status = :upgrade_status, "
                                 "status_updated_time_UTC = :status_time ,"
                                 "transfer_end_time_UTC = :end_time ",
                ExpressionAttributeValues={
                    ':status': device_transfer.get_transfer_status(),
                    ':upgrade_status': device_transfer.get_firmware_upgrade_status(),
                    ':end_time': device_transfer.get_transfer_end_time_UTC(),
                    ':status_time': device_transfer.get_status_updated_time_UTC()
                },
                ReturnValues="ALL_NEW"  # You can adjust the return values as needed
            )
        except Exception as e:
            # Handle the exception according to your requirements
            print(f"Error updating item: {e}")

    def update_device_transfer_progress_pct(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object in the DeviceTransfers table.

        param deviceTransfer: Updated DeviceTransfer object.
        """
        try:
            self._table.update_item(
                Key={
                    'device_id': device_transfer.get_device_id(),
                    'task_id': device_transfer.get_task_id()
                },
                UpdateExpression="SET progress_pct = :progress_pct ",
                ExpressionAttributeValues={
                    ':progress_pct': device_transfer.get_progress_pct()
                },
                ReturnValues="ALL_NEW"  # You can adjust the return values as needed
            )
        except Exception as e:
            # Handle the exception according to your requirements
            print(f"Error updating item: {e}")

    def update_device_transfer_firmware_version(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object in the DeviceTransfers table.

        param deviceTransfer: Updated DeviceTransfer object.
        """
        try:
            self._table.update_item(
                Key={
                    'device_id': device_transfer.get_device_id(),
                    'task_id': device_transfer.get_task_id()
                },
                UpdateExpression="SET firmware_version = :firmware_version ",
                ExpressionAttributeValues={
                    ':firmware_version': device_transfer.get_firmware_version()
                },
                ReturnValues="ALL_NEW"  # You can adjust the return values as needed
            )
        except Exception as e:
            # Handle the exception according to your requirements
            print(f"Error updating item: {e}")

    # -----------------
    # Update operations
    # -----------------
    def update_device_transfer(self, device_transfer: DeviceTransfer):
        """
        Updates deviceTransfer object to the DeviceTransfer table.

        :param deviceTransfer:  deviceTransfer object.
        :return:                Updated DeviceTransfer object.
        """
        try:
            self._table.put_item(Item=device_transfer.to_dict())
        except ClientError as err:
            logger.error(
                f'Error while calling update_device_transfer for deviceId: {device_transfer._device_id}: {err}'
            )
            raise
        else:
            return device_transfer