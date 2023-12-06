# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Class for encoding/decoding Sidewalk Sensor Monitoring Demo Application payload tags.
"""
from protocol import *
from textwrap import wrap


class Tag:
    """
    A class representing Sidewalk Sensor Monitoring Demo Application payload tag.
    Used for tags decoding/encoding.

    Attributes
    ----------
        format: str
            Binary string representing TLV format.
        type: str
            Binary string representing tag type.
        val_len: str
            Binary string representing payload value length.
        val: str
            Binary string representing payload value.
        json: dict
            Dictionary, which presents above-mentioned attributes in human-readable format.
    """

    def __init__(self):
        self.type = ""
        self.format = ""
        self.val = ""
        self.val_len = ""
        self.json = {}

    def decode(self, type: str, format: str, val: str, val_len: str = ""):
        """
        Decodes Tag object based on input parameters.

        :param type:        TagType (binary string).
        :param format:      TLV format (binary string).
        :param val:         Payload value (binary string).
        :param val_len:     Payload length (if TLV format is STANDARD, binary string).
        :return:            Tag object.

        """
        self.type = type
        self.format = format
        self.val = val
        self.val_len = val_len
        self._decode_tag()
        return self

    def encode(self, json: dict):
        """
        Encodes Tag object based on input dictionary.

        :param json:        Dict of the following structure: {TagType: value}.
        :return:            Tag object.
        """
        self.json = json
        self._encode_tag()
        return self

    def dict_repr(self):
        """
        Returns dict representation of the Tag object.
        :return:    Dict representing Tag object.
        """
        return {
            "format": TlvFormat(self.format).name,
            "type": TagType(self.type).name,
            "val_len": self.val_len,
            "val": self.val,
            "json": self.json,
        }

    def bin_repr(self):
        """
        Returns binary representation of the Tag object.
        :return:    Binary string representing Tag object.
        """
        return self.format + self.type + self.val_len + self.val

    def _decode_tag(self):
        """
        Decodes tag value into human readable json and stores it in json attribute.
        """
        fn = Tag.DECODERS_MAP.get(TagType(self.type))
        try:
            self.json = fn(self)
        except TypeError:
            self.json = {}

    def _encode_tag(self):
        """
        Decomposes human readable json into format, type, val_len and val components
        and stores them in corresponding attributes.
        """
        tag_type = list(self.json.keys())[0]
        self.type = TagType(tag_type).value
        fn = Tag.ENCODERS_MAP.get(tag_type)
        try:
            self.val = fn(self)
            val_len = int(len(self.val) / 8)  # get value size in bytes
            if val_len == 1:
                self.format = TlvFormat.SIZE_OPTIMIZED_1B.value
                self.val_len = ""
            elif val_len == 2:
                self.format = TlvFormat.SIZE_OPTIMIZED_2B.value
                self.val_len = ""
            elif val_len == 4:
                self.format = TlvFormat.SIZE_OPTIMIZED_4B.value
                self.val_len = ""
            else:
                self.format = TlvFormat.STANDARD.value
                self.val_len = format(val_len, "08b")
        except TypeError as e:
            self.format = ""
            self.type = ""
            self.val_len = ""
            self.val = ""

    # -------------
    # Tag decoders
    # -------------
    def _decode_button_press(self):
        """
        Decodes BUTTON_PRESS tag and turns it into a human-readable dict.
        :return:    Dict representing received "button pressed" event.
        """
        return {"button_press": [int(id, 2) for id in wrap(self.val, 8)]}

    def _decode_current_gps_time_in_secs(self):
        """
        Decodes CURRENT_GPS_TIME_IN_SECS tag and turns it into a human-readable dict.
        :return:    Dict representing current gps time.
        """
        return {"gps_time": int(self.val, 2)}

    def _decode_downlink_latency_in_secs(self):
        """
        Decodes DL_LATENCY_IN_SECS tag and turns it into a human-readable dict.
        :return:    Dict representing downlink latency.
        """
        return {"dl_latency": int(self.val, 2)}

    def _decode_led_on_resp(self):
        """
        Decodes TAG_LED_ON_RESP tag and turns it into a human-readable dict.
        :return:    Dict representing received "LEDs on" response.
        """
        return {"led_on_resp": [int(id, 2) for id in wrap(self.val, 8)]}

    def _decode_led_off_resp(self):
        """
        Decodes TAG_LED_OFF_RESP tag and turns it into a human-readable dict.
        :return:    Dict representing received "LEDs off" response.
        """
        return {"led_off_resp": [int(id, 2) for id in wrap(self.val, 8)]}

    def _decode_link_type(self):
        """
        Decodes LINK_TYPE tag and turns it into a human-readable dict.
        :return:    Dict representing link type.
        """
        return {"link_type": LinkType(self.val).name}

    def _decode_number_of_buttons(self):
        """
        Decodes NUMBER_OF_BUTTONS tag and turns it into a human-readable dict.
        :return:    Dict representing number of available buttons.
        """
        return {"buttons": [int(id, 2) for id in wrap(self.val, 8)]}

    def _decode_number_of_leds(self):
        """
        Decodes NUMBER_OF_LEDS tag and turns it into a human-readable dict.
        :return:    Dict representing number of available LEDs.
        """
        return {"leds": [int(id, 2) for id in wrap(self.val, 8)]}

    def _decode_temp_sensor_available_and_unit_representation(self):
        """
        Decodes TEMP_SENSOR_AVAILABLE_AND_UNIT_REPRESENTATION tag and turns it into a human-readable dict.
        :return:    Dict representing temp sensor metadata.
        """
        return {
            "sensor": True if self.val[-1] == "1" else False,
            "sensor_units": SensorUnits(self.val[-2]).name,
        }

    def _decode_temp_sensor_data(self):
        """
        Decodes TEMP_SENSOR_DATA tag and turns it into a human-readable dict.
        :return:    Dict representing temp sensor data.
        """
        return {"sensor_data": int(self.val, 2)}

    def _decode_ota_supported(self):
        """
        Decodes OTA_SUPPORTED tag and turns it into a human-readable dict.
        :return: Dict representing ota support
        """
        return {"ota_supported": int(self.val, 2)}

    def _decode_ota_firmware_version(self):
        """
        Decodes OTA_FIRMWARE_VERSION tag and turns it into a human-readable dict.
        :return: Dict representing firmware version
        """
        vals = wrap(self.val, 16)
        return {"major": int(vals[0], 2), "minor": int(vals[1], 2)}

    def _decode_ota_trigger_notify(self):
        """
        Decodes OTA_TRIGGER_NOTIFY tag and turns it into human-readable dict.
        :return: Dict representing request for an OTA trigger
        """
        return {"ota_trigger": int(self.val, 2)}

    def _decode_ota_progress(self):
        """
        Decodes OTA_PROGRESS tag and turns it into human-readable dict.
        :return: Dict representing OTA Progress
        """
        return {
            "ota_percent": int(self.val[:8], 2),
            "completed_file_size": int(self.val[8:24], 2),
            "total_file_size": int(self.val[24:], 2),
        }

    def _decode_ota_file_id(self):
        """
        Decodes OTA_FILE_ID tag and turns it into human-readable dict.
        :return: Dict representing an OTA file id
        """
        return {"file_id": int(self.val, 2)}

    def _decode_ota_completion_status(self):
        """
        Decodes OTA_COMPLETION_STATUS tag and turns it into human-readable dict.
        :return: Dict representing OTA completion status
        """
        return {"ota_status": OtaCompletionStatus(self.val).name}

    DECODERS_MAP = {
        TagType.BUTTON_PRESS: _decode_button_press,
        TagType.CURRENT_GPS_TIME_IN_SECS: _decode_current_gps_time_in_secs,
        TagType.DL_LATENCY_IN_SECS: _decode_downlink_latency_in_secs,
        TagType.LED_ON_RESP: _decode_led_on_resp,
        TagType.LED_OFF_RESP: _decode_led_off_resp,
        TagType.LINK_TYPE: _decode_link_type,
        TagType.NUMBER_OF_BUTTONS: _decode_number_of_buttons,
        TagType.NUMBER_OF_LEDS: _decode_number_of_leds,
        TagType.TEMP_SENSOR_AVAILABLE_AND_UNIT_REPRESENTATION: _decode_temp_sensor_available_and_unit_representation,
        TagType.TEMP_SENSOR_DATA: _decode_temp_sensor_data,
        TagType.OTA_SUPPORTED: _decode_ota_supported,
        TagType.OTA_FIRMWARE_VERSION: _decode_ota_firmware_version,
        TagType.OTA_TRIGGER_NOTIFY: _decode_ota_trigger_notify,
        TagType.OTA_PROGRESS: _decode_ota_progress,
        TagType.OTA_COMPLETION_STATUS: _decode_ota_completion_status,
        TagType.OTA_FILE_ID: _decode_ota_file_id,
    }

    # -------------
    # Tag encoders
    # -------------
    def _encode_button_pressed_resp(self):
        """
        Encodes BUTTON_PRESSED_RESP tag value based on json dict.
        :return:    Tag value (binary string).
        """
        indices = self.json[TagType.BUTTON_PRESSED_RESP]
        return "".join([format(idx, "08b") for idx in indices])

    def _encode_led_on(self):
        """
        Encodes LED_ON tag value based on json dict.
        :return:    Tag value (binary string).
        """
        indices = self.json[TagType.LED_ON]
        return "".join([format(idx, "08b") for idx in indices])

    def _encode_led_off(self):
        """
        Encodes LED_OFF tag value based on json dict.
        :return:    Tag value (binary string).
        """
        indices = self.json[TagType.LED_OFF]
        return "".join([format(idx, "08b") for idx in indices])

    def _encode_current_gps_time_in_secs(self):
        """
        Encodes CURRENT_GPS_TIME_IN_SECS tag value based on json dict.
        :return:    Tag value (binary string).
        """
        current_gps_time = self.json[TagType.CURRENT_GPS_TIME_IN_SECS]
        return format(current_gps_time, "032b")

    ENCODERS_MAP = {
        TagType.BUTTON_PRESSED_RESP: _encode_button_pressed_resp,
        TagType.LED_ON: _encode_led_on,
        TagType.LED_OFF: _encode_led_off,
        TagType.CURRENT_GPS_TIME_IN_SECS: _encode_current_gps_time_in_secs,
    }
