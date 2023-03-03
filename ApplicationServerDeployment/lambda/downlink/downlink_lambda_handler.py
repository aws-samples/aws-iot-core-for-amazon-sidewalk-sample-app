# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Handles requests to send downlink commands to a wireless device.
"""

import base64
import boto3
import json
import cors_utils
import traceback
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from typing import Final

import time_utils
from command import Command
from protocol import *
from tag import Tag


COMMAND_KEY: Final = "command"
DEMO_APP_CAP_DISCOVERY_RESP: Final = "DEMO_APP_CAP_DISCOVERY_RESP"
DEMO_APP_ACTION_RESP: Final = "DEMO_APP_ACTION_RESP"
DEMO_APP_ACTION_REQ: Final = "DEMO_APP_ACTION_REQ"
session = boto3.Session()
wireless_client = session.client(service_name='iotwireless')
headers = {
    "Access-Control-Allow-Origin": cors_utils.get_gui_bucket_url_for_cors(),
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS,PUT",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}


def send_hex_payload_to_device(wireless_device_id: str, cmd: Command, seq_n: int):
    """
    Extracts hexadecimal representation of the Command object.
    Encodes hex into base64 and sends it to the wireless device.

    :param wireless_device_id:  Id of the wireless device.
    :param cmd:                 Command object.
    :param seq_n:               Sequence number of the downlink message.
    :return:                    IoTWireless client response.
    """
    wireless_metadata = {}
    wireless_metadata_sidewalk = {"Seq": seq_n}
    wireless_metadata["Sidewalk"] = wireless_metadata_sidewalk

    payload_hex = cmd.hex_repr()
    payload_data = base64.b64encode(bytes.fromhex(payload_hex)).decode()

    return wireless_client.send_data_to_wireless_device(Id=wireless_device_id,
                                                        TransmitMode=0,
                                                        PayloadData=payload_data,
                                                        WirelessMetadata=wireless_metadata)


def calculate_seq_from_current_time():
    """
    Determines sequence number to be used for downlink message based on the current time.
    SeqN is calculated in following fashion:
    First 2 digits are reserved for current seconds
    Last 2 digits are reserved for first 2 digits of current microseconds

    :return:    Sequence number.
    """
    time_now = datetime.now(timezone.utc)
    seq_n = time_now.strftime("%S%f")[:-4]
    while seq_n[0] == "0" and len(seq_n) > 1:
        seq_n = seq_n[1:]
    return int(seq_n)


def format_command_id_as_json(command: str, response):
    """
    Formats information about the sent downlink into a json dict.

    :param command:     Demo app specific command.
    :param response:    IoTWireless client response.
    :return:            Command data in a json format.
    """
    dict_format = dict()
    dict_format["command"] = command
    dict_format["response"] = response
    return dict_format


def lambda_handler(event, context):
    """
    Handles requests to send downlink commands to a wireless device.
    """
    device_id = ""
    try:
        # ---------------------------------------------------------------
        # Receive and record incoming event in the CloudWatch log group.
        # Read its payload.
        # ---------------------------------------------------------------
        if type(event) == str:
            event = json.loads(event)

        method = event.get("httpMethod")
        if method != "POST":
            return {
                'statusCode': 400,
                'body': json.dumps('Only POST requests are supported'),
                "headers": headers
            }

        body = event.get("body")
        print(f'Received request: {body}')
        if body is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Body field is missing'),
                "headers": headers
            }

        if type(body) == dict:
            # Uplink lambda is sending body as dict not string.
            # When passing body as string all "" are replaced by '' which breaks json.loads.
            json_body = body
        else:
            json_body = json.loads(body)

        command = json_body.get("command")
        device_id = json_body.get("deviceId")

        seq_n = calculate_seq_from_current_time()

        # ---------------------------------------------
        # Handle and encode demo app specific commands
        # ---------------------------------------------
        if command == DEMO_APP_CAP_DISCOVERY_RESP:
            status_code = '00000000'
            cmd = Command()
            cmd.encode(
                status_hdr_ind=True,
                op_code=OpCode.MSG_TYPE_RESP,
                cls=Class.DEMO_APP_CLASS,
                id=Id.DEMO_APP_CAP_DISCOVERY_RESP,
                status_code=status_code
            )
            msg_id = send_hex_payload_to_device(device_id, cmd, seq_n)

            return {
                'statusCode': 200,
                'body': json.dumps(format_command_id_as_json(DEMO_APP_CAP_DISCOVERY_RESP, msg_id)),
                "headers": headers
            }

        elif command == DEMO_APP_ACTION_RESP:
            button_press = json_body.get("button_press")
            tags_json = [{TagType.BUTTON_PRESSED_RESP: button_press}]
            tags = [Tag().encode(tag) for tag in tags_json]
            cmd = Command().encode(
                status_hdr_ind=True,
                op_code=OpCode.MSG_TYPE_RESP,
                cls=Class.DEMO_APP_CLASS,
                id=Id.DEMO_APP_ACTION_RESP,
                status_code='00000000',
                payload=tags
            )
            msg_id = send_hex_payload_to_device(device_id, cmd, seq_n)
            return {
                'statusCode': 200,
                'body': json.dumps(format_command_id_as_json(DEMO_APP_ACTION_RESP, msg_id)),
                "headers": headers
            }
        elif command == DEMO_APP_ACTION_REQ:

            led_id = json_body.get("ledId")
            action = json_body.get("action")
            gps_time = time_utils.get_gps_time()
            if action == "ON":
                tag_type = TagType.LED_ON
            elif action == "OFF":
                tag_type = TagType.LED_OFF
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f"Command {str(command)} received unsupported action {action}."
                                       f" Action needs to be either ON or OFF. "),
                    "headers": headers
                }
            if type(led_id) is not list:
                if type(led_id) is int:
                    led_id = [led_id]
                else:
                    return {
                        'statusCode': 400,
                        'body': json.dumps("Led index of format {} is not supported. "
                                "Only lists and int are supported".format(type(led_id))),
                        "headers": headers
                    }
            tags_json = [
                {tag_type: led_id},
                {TagType.CURRENT_GPS_TIME_IN_SECS: int(gps_time)}
            ]
            tags = [Tag().encode(tag) for tag in tags_json]
            cmd = Command().encode(
                status_hdr_ind=False,
                op_code=OpCode.MSG_TYPE_WRITE,
                cls=Class.DEMO_APP_CLASS,
                id=Id.DEMO_APP_ACTION_REQ,
                payload=tags
            )
            msg_id = send_hex_payload_to_device(device_id, cmd, seq_n)
            return {
                'statusCode': 200,
                'body': json.dumps(format_command_id_as_json(DEMO_APP_ACTION_REQ, msg_id)),
                "headers": headers
            }
        elif command is None:
            return {
                'statusCode': 400,
                'body': json.dumps('Command field is missing.'),
                "headers": headers
            }

        return {
            'statusCode': 400,
            'body': json.dumps('Command ' + str(command) + ' is not supported.'),
            "headers": headers
        }
    except ClientError as error:
        print(f'Iot wireless exception: {traceback.format_exc()}.')
        if error.response['Error']['Code'] == 'ResourceNotFoundException':
            return {
                'statusCode': 400,
                'body': json.dumps('Device with id {} was not found.'.format(device_id)),
                "headers": headers
            }
        elif error.response['Error']['Code'] == 'ValidationException':
            return {
                'statusCode': 400,
                'body': json.dumps('Validation of device with id {} failed with message {}.'.format(device_id, error)),
                "headers": headers
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps('Iot wireless returned exception {}.'.format(error)),
                "headers": headers
            }

    except Exception:
        print(f'Unexpected error occurred: {traceback.format_exc()}')
        return {
            'statusCode': 500,
            'body': json.dumps('Unexpected error occurred: ' + traceback.format_exc()),
            "headers": headers
        }
