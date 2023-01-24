# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


import argparse
import boto3
import json
import logging
import os
import random
import string
from libs.ProvisionWrapper import ProvisionWrapper, InputType
from libs.EnvConfig import EnvConfig

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ENDPOINT = {
    'prod': 'https://api.iotwireless.us-east-1.amazonaws.com',
    'gamma': 'https://api.gamma.us-east-1.iotwireless.iot.aws.dev',
}


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-i', '--instances', help="Number of instances to generate (default: 1)", required=False,
                        default=1)
    args = parser.parse_args()

    e = EnvConfig("../config.yaml")

    aws = AWSHandler(e.env, e.aws_profile).client

    if not e.device_profile_id:
        profile_name = 'prototype_' + ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        logger.info(f"No DeviceProfileID specified. Creating a new DeviceProfile with random name {profile_name}")
        response = aws.create_device_profile(Sidewalk={}, Name=profile_name)
        print_response(response)
        print_status_code(response)
        device_profile_id = response["Id"]
        logger.info(f"Profile created, {device_profile_id}")
        e.update_profile_id(device_profile_id)

    logger.info(f"Getting a DeviceProfile by Id {e.device_profile_id}")
    response = aws.get_device_profile(Id=e.device_profile_id)
    print_response(response)
    print_status_code(response)
    del response["ResponseMetadata"]

    logger.info("Saving device profile to file")
    paths = PathsWrapper(e.device_profile_id)
    paths.save_profile_json(response)
    logger.info(f"Saved DeviceProfile details to {paths.get_profile_json_filepath()}")

    for instanceNr in range(0, int(args.instances)):
        logger.info(f"Creating a new WirelessDevice (instance nr {instanceNr})")
        response = aws.create_wireless_device(Type='Sidewalk',
                                              DestinationName=e.destination_name,
                                              Sidewalk={"DeviceProfileId": e.device_profile_id})
        print_response(response)
        print_status_code(response)
        wireless_device_id = response["Id"]

        logger.info(f"Getting a WirelessDevice by Id {wireless_device_id}")
        response = aws.get_wireless_device(Identifier=wireless_device_id, IdentifierType="WirelessDeviceId")
        print_response(response)
        print_status_code(response)
        del response["ResponseMetadata"]

        logger.info("Saving wireless device to file")
        paths.save_device_json(wireless_device_id, response)

        logger.info("Generating MFG by calling provision.py")
        p = ProvisionWrapper(script_dir=e.provision_script_directory, arm_toolchain_dir=e.arm_toolchain_dir,
                             silabs_commander_dir=e.commander_dir, hardware_platform=e.hardware_platform)
        p.generate_mfg(wireless_device_path=paths.get_device_json_filepath(wireless_device_id, absPath=True),
                       device_profile_path=paths.get_profile_json_filepath(absPath=True),
                       input_type=InputType.AWS_API_JSONS,
                       output_dir=paths.get_device_dir(wireless_device_id, absPath=True))
        logger.info("Done!")


def make_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    except OSError as err:
        logger.error(f"An error has occurred: {err}")
        raise


class PathsWrapper:
    def __init__(self, device_profile_id):
        self.device_profile_dir = os.path.join("DeviceProfile_" + device_profile_id)
        make_dir(self.device_profile_dir)

    def get_profile_dir(self):
        return self.device_profile_dir

    def get_profile_json_filepath(self, absPath=False):
        p = os.path.join(self.device_profile_dir, "DeviceProfile.json")
        if absPath:
            return os.path.abspath(p)
        return p

    def save_profile_json(self, data):
        with open(self.get_profile_json_filepath(), 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def get_device_dir(self, device_id, absPath=False):
        p = os.path.join(self.get_profile_dir(), "WirelessDevice_" + device_id)
        if absPath:
            return os.path.abspath(p)
        return p

    def get_device_json_filepath(self, device_id, absPath=False):
        p = os.path.join(self.get_device_dir(device_id), "WirelessDevice.json")
        if absPath:
            return os.path.abspath(p)
        return p

    def save_device_json(self, device_id, data):
        make_dir(self.get_device_dir(device_id))
        with open(self.get_device_json_filepath(device_id), 'w') as outfile:
            json.dump(data, outfile, indent=4)


class AWSHandler:
    def __init__(self, env, profile_name='default'):
        self.env = env
        self.session = boto3.Session(profile_name=profile_name)
        self.client = self.session.client('iotwireless', endpoint_url=ENDPOINT[env])


def print_response(api_response):
    logger.info(json.dumps(api_response, indent=2))


def get_status_code(api_response):
    code = api_response.get("ResponseMetadata").get("HTTPStatusCode")
    return code


def print_status_code(api_response):
    code = get_status_code(api_response)
    logger.info(f"Status: {code}")


main()
