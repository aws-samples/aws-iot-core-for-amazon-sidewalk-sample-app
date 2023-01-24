# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import traceback

import boto3
from datetime import datetime, timezone

from measurement import Measurement


class MeasurementsHandler:
    """
    A class that provides read and write methods for the Measurements table.
    """

    DATABASE_NAME = 'SidewalkTimestream'
    TABLE_NAME = 'Measurements'

    def __init__(self):
        self._boto3_query_client = boto3.client('timestream-query')
        self._boto3_write_client = boto3.client('timestream-write')

    # ----------------
    # Read operations
    # ----------------
    def get_measurements(
            self, wireless_device_id: str, time_range_start: int, time_range_end: int
    ) -> [Measurement]:
        """
        Queries Measurements table for the records coming from given device withing a given time span.

        :param wireless_device_id:  Id of the wireless device.
        :param time_range_start:    Start time (UTC time in seconds).
        :param time_range_end:      End time (UTC time in seconds).
        :return:                    List of Measurement objects.
        """
        query = "SELECT * " \
                "FROM \"SidewalkTimestream\".\"Measurements\" " \
                "WHERE \"wireless_device_id\" = '{}' AND time between '{}' AND '{}'"
        return self._run_query(
            query.format(
                wireless_device_id,
                datetime.fromtimestamp(time_range_start, tz=timezone.utc),
                datetime.fromtimestamp(time_range_end, tz=timezone.utc)
            )
        )

    # -----------------
    # Write operations
    # -----------------
    def add_measurement(self, measurement: Measurement):
        """
        Writes Measurement object into the Measurements table.

        :param measurement: Measurement object.
        """
        self._boto3_write_client.write_records(
            DatabaseName=self.DATABASE_NAME,
            TableName=self.TABLE_NAME,
            Records=[
                {
                    'Time': str(measurement.get_time()),
                    'TimeUnit': 'MILLISECONDS',
                    'Dimensions': [
                        {
                            'Name': 'wireless_device_id',
                            'Value': measurement.get_wireless_device_id()
                        }
                    ],
                    'MeasureName': "temperature",
                    'MeasureValue': str(measurement.get_value()),
                    'MeasureValueType': 'DOUBLE'
                }
            ]
        )

    # -----------------
    # For internal use
    # -----------------
    def _run_query(self, query: str) -> [Measurement]:
        measurements: [Measurement] = []
        try:
            pages = []
            paginator = self._boto3_query_client.get_paginator('query')
            page_iterator = paginator.paginate(QueryString=query)
            for page in page_iterator:
                pages.append(page)

            for page in pages:
                wireless_device_id_position = None
                time_position = None
                measure_value_position = None

                column_info = page['ColumnInfo']

                for position, column in enumerate(column_info):
                    name = column['Name']

                    if name == 'wireless_device_id':
                        wireless_device_id_position = position
                    elif name == 'time':
                        time_position = position
                    elif name == 'measure_value::double':
                        measure_value_position = position

                rows = page['Rows']
                for row in rows:
                    data: list = row['Data']
                    wireless_device_id: str = ""
                    measure_value = None
                    timestamp = 0

                    if 'ScalarValue' in data[wireless_device_id_position]:
                        wireless_device_id = data[wireless_device_id_position]['ScalarValue']

                    if 'ScalarValue' in data[measure_value_position]:
                        measure_value = data[measure_value_position]['ScalarValue']

                    if 'ScalarValue' in data[time_position]:
                        timestamp = int(round(
                            datetime.strptime(data[time_position]['ScalarValue'][:-3], "%Y-%m-%d %H:%M:%S.%f")
                            .replace(tzinfo=timezone.utc)
                            .timestamp() * 1000
                        ))

                    measurement: Measurement = Measurement(wireless_device_id, measure_value, timestamp)
                    measurements.append(measurement)
        except Exception:
            print(f'Unexpected error occurred while fetching measurements: {traceback.format_exc()}')

        return measurements
