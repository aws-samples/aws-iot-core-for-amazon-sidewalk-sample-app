# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Sidewalk Sensor Monitoring Application - protocol constants.
"""

from enum import Enum


class OpCode(Enum):
    """
    Represents Operation Code values.
    """

    MSG_TYPE_READ = "00"
    MSG_TYPE_WRITE = "01"
    MSG_TYPE_NOTIFY = "10"
    MSG_TYPE_RESP = "11"


class Class(Enum):
    """
    Represents Command Class values.
    """

    DEMO_APP_CLASS = "00"


class ClassCmdId(Enum):
    """
    Represents Class Command Id subsets.
    """

    DEMO_APP_CLASS_CMD_CAP_DISCOVERY_ID = "000"
    DEMO_APP_CLASS_CMD_ACTION = "001"


class Id(Enum):
    """
    Represents Command Id values.
    """

    DEMO_APP_CAP_DISCOVERY_NOTIFICATION = "010"
    DEMO_APP_CAP_DISCOVERY_RESP = "011"
    DEMO_APP_ACTION_REQ = "101"
    DEMO_APP_ACTION_NOTIFICATION = "110"
    DEMO_APP_ACTION_RESP = "111"


class TagType(Enum):
    """
    Represents Tag Type values.
    """

    NUMBER_OF_BUTTONS = "000001"
    NUMBER_OF_LEDS = "000010"
    LED_ON = "000011"
    LED_OFF = "000100"
    BUTTON_PRESS = "000101"
    TEMP_SENSOR_DATA = "000110"
    CURRENT_GPS_TIME_IN_SECS = "000111"
    DL_LATENCY_IN_SECS = "001000"
    LED_ON_RESP = "001001"
    LED_OFF_RESP = "001010"
    TEMP_SENSOR_AVAILABLE_AND_UNIT_REPRESENTATION = "001011"
    LINK_TYPE = "001100"
    BUTTON_PRESSED_RESP = "001101"
    OTA_SUPPORTED = "001110"
    OTA_FIRMWARE_VERSION = "001111"
    OTA_TRIGGER_NOTIFY = "010000"
    OTA_PROGRESS = "010001"
    OTA_COMPLETION_STATUS = "010010"
    OTA_FILE_ID = "010011"


class TlvFormat(Enum):
    """
    Represents Tag-Length-Value format values.
    """

    SIZE_OPTIMIZED_1B = "00"
    SIZE_OPTIMIZED_2B = "01"
    SIZE_OPTIMIZED_4B = "10"
    STANDARD = "11"


class LinkType(Enum):
    """
    Represents Link Type values.
    """

    BLE = "00000001"
    FSK = "00000010"
    LORA = "00000100"


class SensorUnits(Enum):
    """
    Represents Temperature Sensor unit values.
    """

    CELSIUS = "0"
    FAHRENHEIT = "1"


class OtaCompletionStatus(Enum):
    """
    Represents Ota completion status
    """

    SUCCESS = "00000001"
    FAILED = "00000010"


"""
Maps Class Cmd Ids to Id subsets.
"""
IdToCmdIdValueMap = {
    Id.DEMO_APP_CAP_DISCOVERY_NOTIFICATION: ClassCmdId.DEMO_APP_CLASS_CMD_CAP_DISCOVERY_ID.value,
    Id.DEMO_APP_CAP_DISCOVERY_RESP: ClassCmdId.DEMO_APP_CLASS_CMD_CAP_DISCOVERY_ID.value,
    Id.DEMO_APP_ACTION_REQ: ClassCmdId.DEMO_APP_CLASS_CMD_ACTION.value,
    Id.DEMO_APP_ACTION_RESP: ClassCmdId.DEMO_APP_CLASS_CMD_ACTION.value,
    Id.DEMO_APP_ACTION_NOTIFICATION: ClassCmdId.DEMO_APP_CLASS_CMD_ACTION.value,
}
