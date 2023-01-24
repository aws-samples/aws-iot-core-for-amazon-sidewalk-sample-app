# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from enum import Enum
from typing import final


@final
class Unit(Enum):
    """
    Class for storing possible sensor unit values.
    """
    CELSIUS = 'CELSIUS'
    FAHRENHEIT = 'FAHRENHEIT'
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        return Unit.UNKNOWN
