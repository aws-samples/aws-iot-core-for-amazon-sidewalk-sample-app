# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import logging
import time
from botocore.exceptions import ClientError

from device import Device
from link_type import LinkType
from unit import Unit


logger = logging.getLogger(__name__)


class SidewalkDevicesHandler:
    """
    A class that provides read and write methods for the SidewalkDevices table.
    """

    TABLE_NAME = 'SidewalkDevices'

    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    # ----------------
    # Read operations
    # ----------------
    def get_device(self, wireless_device_id) -> Device:
        """
        Gets records from the SidewalkDevices table for a particular device.

        :param wireless_device_id:  Wireless device ID.
        :return:                    Device object.
        """
        try:
            response = self._table.get_item(Key={'wireless_device_id': wireless_device_id})
        except ClientError as err:
            logger.error(f'Error while calling get_device for wireless_device_id: {wireless_device_id}: {err}')
            raise
        else:
            if 'Item' in response:
                return Device(**response['Item'])

    def get_all_devices(self) -> [Device]:
        """
        Gets all available records from the SidewalkDevices table.

        :return:    List of Device objects.
        """
        items = []
        try:
            response = self._table.scan()
            items.extend(response.get('Items', []))
            while "NextToken" in response:
                response = self._table.scan(NextToken=response["NextToken"])
                items.extend(response.get('Items', []))
        except ClientError as err:
            logger.error(f'Error while calling get_all_devices: {err}')
            raise
        else:
            devices = []
            for item in items:
                device = Device(**item)
                devices.append(device)
            return devices

    # -----------------
    # Write operations
    # -----------------
    def add_device(self, device) -> Device:
        """
        Adds Device object to the SidewalkDevices table.

        _last_uplink and _time_to_live attributes are ignored.
        last_uplink field is set to the current time.
        time_to_live field is set to the current_time + 24 hours.

        :param device:  Device object.
        :return:        Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            self._table.put_item(
                Item={
                    'wireless_device_id': device.get_wireless_device_id(),
                    'led': device.get_led(),
                    'led_on': device.get_led_on(),
                    'button': device.get_button(),
                    'button_pressed': device.get_button_pressed(),
                    'link_type': device.get_link_type().value,
                    'sensor': device.is_sensor(),
                    'sensor_unit': device.get_sensor_unit().value,
                    'last_uplink': int(time.time()),
                    'time_to_live': ttl
                },
                ReturnValues="ALL_OLD"
            )
        except ClientError as err:
            logger.error(
                f'Error while calling add_device for wireless_device_id: {device.get_wireless_device_id()}: {err}'
            )
            raise
        else:
            device._time_to_live = ttl
            return device

    def update_device(self, wireless_device_id: str, led_on: [int], button_pressed: dict,
                      link_type: LinkType, is_sensor: bool, sensor_unit: Unit) -> Device:
        """
        Updates record in the SidewalkDevices table based on provided parameters.

        :param wireless_device_id:  Wireless device ID.
        :param led_on:              List of indices of the LEDs, which are turned on.
        :param button_pressed:      List of dicts indicating buttons state, see: Device class.
        :param link_type:           LinkType object.
        :param is_sensor:           True if sensor is available on the board, False otherwise.
        :param sensor_unit:         Enum that describes sensor units.
        :return:                    Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            response = self._table.update_item(
                Key={'wireless_device_id': wireless_device_id},
                UpdateExpression="set "
                                 "led_on=:led_on, "
                                 "button_pressed=:button_pressed, "
                                 "link_type=:link_type, "
                                 "sensor=:sensor, "
                                 "sensor_unit=:sensor_unit, "
                                 "last_uplink=:last_uplink, "
                                 "time_to_live=:TTL",
                ExpressionAttributeValues={
                    ':led_on': led_on,
                    ':button_pressed': button_pressed,
                    ':link_type': link_type.name,
                    ':sensor': is_sensor,
                    ':sensor_unit': sensor_unit.value,
                    ':last_uplink': int(time.time()),
                    ':TTL': ttl
                },
                ReturnValues="ALL_NEW")
        except ClientError as err:
            logger.error(f'Error while calling update_device for wireless_device_id: {wireless_device_id}: {err}')
            raise
        else:
            return Device(**response['Attributes'])

    def update_link_type_and_last_uplink(self, wireless_device_id: str, link_type: LinkType) -> Device:
        """
        Updates link_type, last_uplink and time_to_live fields of the record stored in SidewalkDevices table.

        :param wireless_device_id:  Wireless device ID.
        :param link_type:           LinkType object.
        :return:                    Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            response = self._table.update_item(
                Key={'wireless_device_id': wireless_device_id},
                UpdateExpression="set last_uplink=:last_uplink, time_to_live=:TTL, link_type=:link_type",
                ExpressionAttributeValues={
                    ':last_uplink': int(time.time()),
                    ':link_type': link_type.name,
                    ':TTL': ttl
                },
                ReturnValues="ALL_NEW")
        except ClientError as err:
            logger.error(f'Error while calling update_link_type_and_last_uplink for wireless_device_id: '
                         f'{wireless_device_id}: {err}')
            raise
        else:
            return Device(**response['Attributes'])

    def update_last_uplink(self, wireless_device_id: str) -> Device:
        """
        Updates last_uplink and time_to_live fields of the record stored in SidewalkDevices table.

        :param wireless_device_id:  Wireless device ID.
        :return:                    Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            response = self._table.update_item(
                Key={'wireless_device_id': wireless_device_id},
                UpdateExpression="set last_uplink=:last_uplink, time_to_live=:TTL",
                ExpressionAttributeValues={
                    ':last_uplink': int(time.time()),
                    ':TTL': ttl
                },
                ReturnValues="ALL_NEW")
        except ClientError as err:
            logger.error(f'Error while calling update_last_uplink for wireless_device_id: {wireless_device_id}: {err}')
            raise
        else:
            return Device(**response['Attributes'])

    def update_button_and_last_uplink(self, wireless_device_id: str, button_pressed: dict) -> Device:
        """
        Updates button_pressed, last_uplink and time_to_live fields of the record stored in SidewalkDevices table.

        :param wireless_device_id:  Wireless device ID.
        :param button_pressed:      List of dicts indicating buttons state, see: Device class.
        :return:                    Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            response = self._table.update_item(
                Key={'wireless_device_id': wireless_device_id},
                UpdateExpression="set last_uplink=:last_uplink, button_pressed=:button_pressed, time_to_live=:TTL",
                ExpressionAttributeValues={
                    ':last_uplink': int(time.time()),
                    ':button_pressed': button_pressed,
                    ':TTL': ttl
                },
                ReturnValues="ALL_NEW")
        except ClientError as err:
            logger.error(f'Error while calling update_button_and_last_uplink for wireless_device_id: '
                         f'{wireless_device_id}: {err}')
            raise
        else:
            return Device(**response['Attributes'])

    def update_led_and_last_uplink(self, wireless_device_id: str, led_on: [int]) -> Device:
        """
        Updates led_on, last_uplink and time_to_live fields of the record stored in SidewalkDevices table.

        :param wireless_device_id:  Wireless device ID.
        :param led_on:              List of indices of the LEDs, which are turned on.
        :return:                    Updated Device object.
        """
        try:
            ttl = self._get_dynamodb_item_time_to_live()
            response = self._table.update_item(
                Key={'wireless_device_id': wireless_device_id},
                UpdateExpression="set last_uplink=:last_uplink, led_on=:led_on, time_to_live=:TTL",
                ExpressionAttributeValues={
                    ':last_uplink': int(time.time()),
                    ':led_on': led_on,
                    ':TTL': ttl
                },
                ReturnValues="ALL_NEW")
        except ClientError as err:
            logger.error(f'Error while calling update_led_and_last_uplink for wireless_device_id: '
                         f'{wireless_device_id}: {err}')
            raise
        else:
            return Device(**response['Attributes'])

    # -----------------
    # For internal use
    # -----------------
    @staticmethod
    def _get_dynamodb_item_time_to_live() -> int:
        return int(time.time() + 24 * 3600)
