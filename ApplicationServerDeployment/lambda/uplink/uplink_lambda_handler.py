# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles uplinks coming from the Sidewalk Sensor Monitoring Demo Application.
"""

from ota_notifications_handler import OTANotificationsHandler
from ota_start_transfer_lambda_handler import OTAStartTransferHandler
from sidewalk_devices_handler import SidewalkDevicesHandler
from measurements_handler import MeasurementsHandler
import base64
import boto3
import json
import traceback
from datetime import datetime, timezone
from typing import Final

import time_utils
from command import Command
from device import Device
from measurement import Measurement

DEMO_APP_CAP_DISCOVERY_RESP: Final = "DEMO_APP_CAP_DISCOVERY_RESP"
DEMO_APP_CAP_DISCOVERY_NOTIFICATION: Final = "DEMO_APP_CAP_DISCOVERY_NOTIFICATION"
DEMO_APP_ACTION_RESP: Final = "DEMO_APP_ACTION_RESP"
DEMO_APP_ACTION_REQ: Final = "DEMO_APP_ACTION_REQ"
DEMO_APP_ACTION_NOTIFICATION: Final = "DEMO_APP_ACTION_NOTIFICATION"


ota_notifications_handler: Final = OTANotificationsHandler()
device_handler: Final = SidewalkDevicesHandler()
measurement_handler: Final = MeasurementsHandler()
ota_start_transfer_handler: Final = OTAStartTransferHandler()


def send_payload_to_downlink_lambda(command: str, wireless_device_id: str, button_pressed=None):
    """
    Sends commands to the SidewalkDownlinkLambda.

    :param command:             Command to be sent.
    :param wireless_device_id:  Id of the wireless device.
    :param button_pressed:      List of indices of the buttons being pressed.
    :return:                    Response from the SidewalkDownlinkLambda.
    """
    client = boto3.client('lambda')
    downlink_payload = '{"body": {' \
                       ' "command":"' + command + '",' \
                                                  ' "deviceId":"' + wireless_device_id + '"'
    if button_pressed is not None:
        downlink_payload += ', "button_press":' + str(button_pressed)
    downlink_payload += '}, ' \
                        '"httpMethod": "POST"' \
                        '}'

    json_body = json.dumps(downlink_payload).encode('utf-8')
    response = client.invoke(FunctionName='SidewalkDownlinkLambda',
                             Payload=json_body)
    response_body = response["Payload"].read().decode()
    print(f'Response from SidewalkDownlinkLambda: {response_body}')
    return response_body


def lambda_handler(event, context):
    """
    Handles events triggered by incoming uplink messages or notifications.
    """
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Read its metadata.
        # Decode payload data.
        # ---------------------------------------------------------------
        print(f'Received event: {event}')

        notification = event.get("notification")
        if notification is not None:
            try:
                ota_notifications_handler.save_fuota_task_notifications(notification)
                return {
                    'statusCode': 200,
                    'body': json.dumps('Notification received')
                }
            except json.JSONDecodeError as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Invalid JSON format in the notification field.')
                }

        uplink = event.get("uplink")
        if uplink is None:
            print("Unsupported request received {}".format(event))
            return {
                'statusCode': 400,
                'body': json.dumps('Unsupported request received. Only uplink and notification are supported')
            }

        wireless_metadata = uplink.get("WirelessMetadata")
        wireless_device_id = uplink.get("WirelessDeviceId")
        sidewalk = wireless_metadata.get("Sidewalk")
        data = uplink.get("PayloadData")

        data_bytes = data.encode('ascii')
        decoded_data = base64.b64decode(data_bytes).decode('ascii')

        # ---------------------------------------------
        # Decode and handle demo app specific commands
        # ---------------------------------------------
        decoder = Command()
        decoded_payload = decoder.decode(decoded_data).decoded_cmd

        ul_time = decoded_payload.get("gps_time", 0)
        ul_latency = 'no latency info'
        datetime_now = datetime.now(timezone.utc)
        if ul_time is not None:
            ul_latency = str(
                (datetime_now - time_utils.convert_gps_to_utc(ul_time)).total_seconds())

        print(f'WirelessDeviceId: {wireless_device_id} DecodedPayload: {decoded_payload} Seqn: {sidewalk.get("Seq")} '
              f'Uplink latency: {ul_latency}')

        command = decoded_payload["id"]
        if command is None or command == "":
            return {
                'statusCode': 400,
                'body': json.dumps('Received no command from request ' + decoded_payload)
            }

        elif command == DEMO_APP_CAP_DISCOVERY_NOTIFICATION:
            led = decoded_payload.get("leds", [])
            buttons = decoded_payload.get("buttons", [])
            sensor = decoded_payload.get("sensor", False)
            sensor_units = decoded_payload.get("sensor_units")
            link_type = decoded_payload.get("link_type")
            fw_version = decoded_payload.get(
                "major", "0") + "." + decoded_payload.get("minor", "0")
            ota_support = decoded_payload.get("ota_supported", False)

            button_pressed = []
            seq_n = sidewalk.get("Seq")
            for button in buttons:
                button_info = {"id": button, "seqN": seq_n, "state": 0}
                button_pressed.append(button_info)
            device = Device(wireless_device_id=wireless_device_id,
                            led=led, led_on=[],
                            button=buttons, button_pressed=button_pressed,
                            link_type=link_type,
                            sensor=sensor, sensor_unit=sensor_units, ota_support=ota_support, fw_version=fw_version)
            device_handler.add_device(device)
            if ota_support is True:
                ota_notifications_handler.update_device_firmware_version(wireless_device_id, fw_version)
            response_body = send_payload_to_downlink_lambda(
                DEMO_APP_CAP_DISCOVERY_RESP, wireless_device_id)
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from DEMO_APP_CAP_DISCOVERY_NOTIFICATION! Resp' +
                                   ' Body: ' + response_body)
            }

        elif command == DEMO_APP_ACTION_RESP:
            dl_latency = decoded_payload.get("dl_latency", 0)
            led_on = decoded_payload.get("led_on_resp", [])
            led_off = decoded_payload.get("led_off_resp", [])

            # get device
            device = device_handler.get_device(wireless_device_id)
            led_on_set = set(device.get_led_on())

            # update leds
            led_on_set.update(led_on)
            led_on_set.difference_update(led_off)
            device.set_led_on(list(led_on_set))
            device_handler.update_led_and_last_uplink(
                device.get_wireless_device_id(),
                device.get_led_on()
            )

            # 'if' introduced in case of edge device time drift
            print(
                f'Downlink latency: {dl_latency if dl_latency < 1000 else 0}')
            return {
                'statusCode': 200,
                'body': json.dumps('Hello from DEMO_APP_ACTION_RESP!')
            }

        elif command == DEMO_APP_ACTION_NOTIFICATION:

            if "sensor_data" in decoded_payload:
                sensor_data = decoded_payload["sensor_data"]
                link_type = decoded_payload["link_type"]
                device = Device(wireless_device_id, link_type=link_type)
                device_handler.update_link_type_and_last_uplink(
                    device.get_wireless_device_id(),
                    device.get_link_type()
                )

                time_now = datetime_now.timestamp()
                measurement = Measurement(wireless_device_id=wireless_device_id,
                                          temperature=sensor_data,
                                          timestamp=int(round(time_now * 1000)))
                measurement_handler.add_measurement(measurement)

            if "button_press" in decoded_payload:
                buttons_pressed = decoded_payload.get("button_press", [])
                seq_n = sidewalk.get("Seq")
                # get device
                device = device_handler.get_device(wireless_device_id)
                device_buttons = device.get_button_pressed()
                for button in device_buttons:
                    if button["id"] in buttons_pressed:
                        if button["seqN"] < seq_n:
                            button["state"] = 1 - button["state"]
                            button["seqN"] = seq_n
                device.button_pressed = device_buttons
                device_handler.update_button_and_last_uplink(
                    device.get_wireless_device_id(),
                    device.button_pressed
                )

                response_body = send_payload_to_downlink_lambda(DEMO_APP_ACTION_RESP, wireless_device_id,
                                                                button_pressed=buttons_pressed)
                return {
                    'statusCode': 200,
                    'body': json.dumps('Hello from DEMO_APP_ACTION_NOTIFICATION! Resp' +
                                       ' Body: ' + response_body)
                }

            # TODO: Add handler to trigger OTA
            if "ota_trigger" in decoded_payload:
                start_transfer_event = {}
                start_transfer_event['body'] = {'startTimeUTC': int(datetime_now.timestamp()), 'deviceIds':[wireless_device_id]}
                print('ota trigerred with event ', start_transfer_event)
                start_ota_resp = ota_start_transfer_handler.lambda_handler(start_transfer_event, None, True)
                print('Start ota response ', start_ota_resp)

            if "ota_percent" in decoded_payload:
                progress_pct = decoded_payload["ota_percent"]
                ota_notifications_handler.update_device_progress_pct(wireless_device_id, progress_pct)

            if "ota_status" in decoded_payload:
                firmware_upgrade_status = decoded_payload["ota_status"]
                ota_notifications_handler.update_device_firmware_upgrade_status(wireless_device_id, firmware_upgrade_status)

            return {
                'statusCode': 200,
                'body': json.dumps('Hello from DEMO_APP_ACTION_NOTIFICATION!')
            }

        else:
            return {
                'statusCode': 400,
                'body': json.dumps('Command ' + command + 'is not supported. Payload ' + decoded_payload)
            }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc())
        }
