# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from typing import final


@final
class Measurement(object):
    """
    A class that represents the Measurements table record.

    Attributes
    ----------
        _wireless_device_id: str
            Measurement source.
        _value: int
            Measured value.
        _time: int
            UTC time in seconds.
    """

    def __init__(self, wireless_device_id, temperature: int = None, timestamp: int = None, time_to_live=None):
        self._wireless_device_id = wireless_device_id
        self._value = temperature
        self._time = timestamp

    def get_wireless_device_id(self) -> str:
        return self._wireless_device_id

    def get_value(self) -> float:
        return float(self._value)

    def get_time(self) -> int:
        return int(self._time)

    def to_dict(self) -> dict:
        """
        Returns dict representation of the Measurement object.

        :return:    Dict representation of the Measurement.
        """
        return {
            'wireless_device_id': self._wireless_device_id,
            'value': self.get_value(),
            'time': self.get_time()
        }
