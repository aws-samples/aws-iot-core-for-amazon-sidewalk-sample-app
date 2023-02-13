# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
import logging
import time

from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

from measurement import Measurement

logger = logging.getLogger(__name__)


class MeasurementsHandler:
    """
    A class that provides read and write methods for the Measurements table.
    """

    TABLE_NAME = 'SidewalkMeasurements'

    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    # ----------------
    # Read operations
    # ----------------

    def get_measurements_for_device(self, wireless_device_id: str) -> [Measurement]:
        """
        Queries Measurements table for the records coming from given device withing a given time span.

        :param wireless_device_id:  Id of the wireless device.
        :return:                    List of Measurement objects.
        """
        items = []
        try:
            response = self._table.scan(IndexName='wireless_device_id',
                                        FilterExpression=Attr('wireless_device_id').eq(wireless_device_id))
            items.extend(response.get('Items', []))
        except ClientError as err:
            logger.error(f'Error while calling get_all_devices: {err}')
            raise
        else:
            measurements = []
            for item in items:
                measurement = Measurement(**item)
                measurements.append(measurement)
            return measurements

    # -----------------
    # Write operations
    # -----------------
    def add_measurement(self, measurement: Measurement):
        """
        Adds measurement object to the SidewalkMeasurement table.

        _time_to_live attribute is ignored.
        time_to_live field is set to the current_time + 24 hours.

        :param measurement:  Measurement object.
        :return:             Updated Measurement object.
        """
        try:
            timestamp = int(time.time())
            ttl = self._get_dynamodb_item_time_to_live(timestamp)
            self._table.put_item(
                Item={
                    'timestamp': timestamp,
                    'wireless_device_id': measurement.get_wireless_device_id(),
                    'temperature': Decimal(measurement.get_value()),
                    'time_to_live': ttl
                },
                ReturnValues="ALL_OLD"
            )
        except ClientError as err:
            logger.error(
                f'Error while calling add_measurement for wireless_device_id: {measurement.get_wireless_device_id()}: {err}'
            )
            raise
        else:
            measurement._time_to_live = ttl
            return measurement

    # -----------------
    # For internal use
    # -----------------
    @staticmethod
    def _get_dynamodb_item_time_to_live(timestamp: int) -> int:
        return timestamp + 3600
