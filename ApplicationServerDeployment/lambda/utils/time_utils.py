# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Utility functions for time conversion.
"""

from datetime import datetime, timezone
from typing import Final

GPS_UTC_DIFF_SECONDS: Final = 315_964_800
LEAP_SECONDS: Final = 18


def convert_gps_to_utc(gps_time: int):
    """
    Converts GPS time to UTC time.

    :param gps_time:    GPS time given in seconds.
    :return:            UTC datetime.
    """
    utc_time = gps_time + GPS_UTC_DIFF_SECONDS - LEAP_SECONDS
    return datetime.fromtimestamp(utc_time, tz=timezone.utc)


def get_gps_time():
    """
    Returns current GPS time.

    :return:    GPS time in seconds.
    """
    dt_from_gps_epoch = (datetime.now(timezone.utc).replace(tzinfo=None) - datetime(1980, 1, 6)).total_seconds()
    return dt_from_gps_epoch + LEAP_SECONDS
