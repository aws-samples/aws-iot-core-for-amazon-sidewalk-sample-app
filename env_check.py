# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

try:
    import boto3

    boto3_installed = True
except:
    boto3_installed = False
import logging
import os
import subprocess
import sys
import yaml

# add ApplicationServerDeployment to path
sys.path.append(os.path.dirname(__file__).join("ApplicationServerDeployment"))
from ApplicationServerDeployment.libs.utils import log_success, log_error, log_check
from EdgeDeviceProvisioning.libs.EnvConfig import EnvConfig
from EdgeDeviceProvisioning.libs.ProvisionWrapper import BoardType

logging.getLogger('botocore').setLevel(logging.CRITICAL)
SUPPORTED_PLATFORMS = ['NORDIC', 'SILABS', 'TI', 'ALL']


def main():
    config_file = "config.yaml"

    log_check("PYTHON VERSION")
    if check_python_version():
        log_success("PASS - python version correct!")
    else:
        log_error(f"FAIL! Your python version ({sys.version_info}) is too old! ")

    log_check("CONFIG.YAML SYNTAX")
    if check_config_is_proper_yaml(config_file):
        log_success(f"PASS - {config_file} parsed with no issues!")
    else:
        log_error(f"FAIL! {config_file} is not a proper YAML file. Please check formatting of the file")
        quit()

    log_check("CONFIG.YAML MANDATORY ATTRIBUTES")
    config_err = evaluate_config_mandatory_fields(config_file)
    if config_err is None:
        log_success("PASS - config.yaml looks good!")
    else:
        log_error(f"FAIL! config.yaml problem. {config_err}")
        quit()


    log_check("BOTO3 INSTALLED")
    if boto3_installed:
        log_success("PASS - boto3 library is installed!")
    else:
        log_error("FAIL! Can't find boto3 library. Did you install requirements.txt?")
        quit()

    e = EnvConfig(config_file)
    log_check("AWS PROFILE")
    if check_aws_profile(e.aws_profile):
        log_success("PASS - profile defined in config.yaml can connect to AWS!")
    else:
        log_error(
            f"FAIL! Can't communicate with AWS using provided profile: '{e.aws_profile}'. Did you configure AWS credentials?")
        quit()

    log_check("BOTO3 VERSION")
    if boto3_supports_sidewalk(e.aws_profile):
        log_success("PASS - boto3 with Sidewalk support installed!")
    else:
        log_error(
            f"FAIL! installed version of boto3 doesn't support Sidewalk AWS APIs. Did you install requirements.txt?")

    if e.hardware_platform in [BoardType.SiLabs, BoardType.All]:
        log_check("SIMPLICITY COMMANDER PRESENCE")
        if check_simplicity_commander_available(location=e.commander_dir):
            log_success("PASS - simplicity commander.exe available!")
        else:
            log_error(
                "FAIL! Unable to find Simplicity Commander! Please install https://community.silabs.com/s/article/simplicity-commander and add the path to config.yaml")


def check_config_is_proper_yaml(config_yaml):
    try:
        with open(config_yaml, 'r') as file:
            yaml.safe_load(file)
            return True
    except:
        return False


def evaluate_config_mandatory_fields(config_yaml):
    with open(config_yaml, 'r') as file:
        config_struct = yaml.safe_load(file)

    if config_struct.get("Config") is None:
        return "'Config' section missing!"
    else:
        if config_struct["Config"].get("AWS_PROFILE") is None:
            return "AWS_PROFILE field missing!"
        if config_struct["Config"].get("DESTINATION_NAME") is None:
            return "DESTINATION_NAME field missing!"
        platform = config_struct["Config"].get("HARDWARE_PLATFORM")
        if platform is None:
            return "HARDWARE_PLATFORM field missing!"
        elif platform not in SUPPORTED_PLATFORMS:
            return f"HARDWARE_PLATFORM value not supported! Available values: {SUPPORTED_PLATFORMS}"

    if config_struct.get("_Paths") is None:
        return "'_Paths' section missing!"
    else:
        if config_struct["_Paths"].get("PROVISION_SCRIPT_DIR") is None:
            return "PROVISION_SCRIPT_DIR field missing!"

    return None


def check_aws_profile(aws_profile_name):
    try:
        session = boto3.Session(profile_name=aws_profile_name)
        session.client('s3')
        return True
    except:
        return False


def check_hardware_platform(platform):
    if platform in SUPPORTED_PLATFORMS:
        return True
    else:
        return False


def check_python_version():
    if sys.version_info >= (3, 6):
        return True
    else:
        return False


def boto3_supports_sidewalk(aws_profile_name):
    try:
        session = boto3.Session(profile_name=aws_profile_name)
        client = session.client('iotwireless')
        return 'Sidewalk' in str(client.list_device_profiles.__doc__)
    except:
        return False


def check_simplicity_commander_available(location=None):
    try:
        subprocess.run(args=["commander", '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True

    except FileNotFoundError:
        if location:
            full_path = os.path.abspath(os.path.join(location, "commander"))
            try:
                subprocess.run(args=[full_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except FileNotFoundError:
                return False
    except:
        return False


main()
