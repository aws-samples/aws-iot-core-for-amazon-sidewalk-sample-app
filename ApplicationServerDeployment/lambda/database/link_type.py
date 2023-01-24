# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from enum import Enum
from typing import final


@final
class LinkType(Enum):
    """
    Class for storing possible LinkType values.
    """

    BLE = 'BLE'
    FSK = 'FSK'
    LORA = 'LORA'
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        return LinkType.UNKNOWN
