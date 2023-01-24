# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from typing import final

from link_type import LinkType
from unit import Unit


@final
class Device(object):
    """
    A class that represents record from the SidewalkDevice table.

    Attributes
    ----------
        _wireless_device_id: str
            Wireless device ID.
        _led: [int]
            List of indices of the LEDs available on the board.
        _led_on: [int]
            List of indices of the LEDs, which are turned on.
        _button: [int]
            List of indices of the buttons available on the board.
        _button_pressed: [dict]
            List of dicts of the following shape:
                {
                    id: int
                        Index of the button.
                    seqN: int
                        Seqn of the last toggle button request.
                    state: int
                        Button state (1 - engaged, 0 - disengaged)
                }
        _link_type: LinkType
            Enum that describes link type.
        _sensor: bool
            True if sensor is available on the board, False otherwise.
        _sensor_unit: Unit
            Enum that describes sensor units.
        _last_uplink: int
            UTC time of last received uplink (in seconds).
        _time_to_live: int
            UTC time when record should be removed from the table (in seconds; equals last_uplink + 24 hours).
    """

    def __init__(self, wireless_device_id, led=None, led_on=None, button=None, button_pressed=None, link_type=None,
                 sensor=False, sensor_unit=None, last_uplink=0, time_to_live=None):

        self._button = [] if button is None else button
        self._led = [] if led is None else led

        self._wireless_device_id = wireless_device_id
        self._link_type = LinkType(link_type)

        self._sensor = sensor
        self._sensor_unit = Unit(sensor_unit)

        self._last_uplink = last_uplink
        self._time_to_live = time_to_live

        self._button_pressed = {} if button_pressed is None else button_pressed
        self._led_on = [] if led_on is None else led_on

    def set_led_on(self, led_on: [int]):
        self._led_on = led_on

    def get_wireless_device_id(self) -> str:
        return self._wireless_device_id

    def get_led(self) -> [int]:
        return [int(x) for x in self._led]

    def get_led_on(self) -> [int]:
        return [int(x) for x in self._led_on]

    def get_button(self) -> [int]:
        return [int(x) for x in self._button]

    def get_button_pressed(self) -> dict:
        return self._button_pressed

    def get_enabled_button_pressed_state(self) -> [int]:
        button_pressed = []
        for button in self.get_button_pressed():
            if button["state"] == 1:
                button_pressed.append(int(button["id"]))
        return button_pressed

    def get_link_type(self) -> LinkType:
        return self._link_type

    def is_sensor(self) -> bool:
        return self._sensor

    def get_sensor_unit(self) -> Unit:
        return self._sensor_unit

    def get_last_uplink(self) -> int:
        return int(self._last_uplink)

    def get_time_to_live(self) -> int:
        return int(self._time_to_live)

    def to_dict(self) -> dict:
        """
        Returns dict representation of the Device object.

        :return:    Dict representation of the Device.
        """
        return {
                'wireless_device_id': self.get_wireless_device_id(),
                'led': self.get_led(),
                'led_on': self.get_led_on(),
                'button': self.get_button(),
                'button_pressed': self.get_enabled_button_pressed_state(),
                'link_type': self.get_link_type().value,
                'sensor': self.is_sensor(),
                'sensor_unit': self.get_sensor_unit().value,
                'last_uplink': self.get_last_uplink(),
                'time_to_live': self.get_time_to_live()
            }
