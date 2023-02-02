# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os

import yaml

from .ProvisionWrapper import BoardType


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class EnvConfig:
    def __init__(self, config_file_name):

        self.config_file = config_file_name
        split_tup = os.path.splitext(self.config_file)
        self.config_file_type = split_tup[1]

        config_struct = self.read_config_file()

        if config_struct.get("Config", None):
            self.env = config_struct["Config"].get("ENV", "prod")
            self.aws_profile = config_struct["Config"].get("AWS_PROFILE", "default")
            self.destination_name = config_struct["Config"].get("DESTINATION_NAME", "SidewalkDestination")
            platform = config_struct["Config"].get("HARDWARE_PLATFORM", "ALL")
        else:
            self.env = "prod"
            self.aws_profile = "default"

            self.destination_name = "SidewalkDestination"
            platform = "ALL"

        if platform == "ALL":
            self.hardware_platform = BoardType.All
        elif platform == 'NORDIC':
            self.hardware_platform = BoardType.Nordic
        elif platform == 'TI':
            self.hardware_platform = BoardType.TI
        elif platform == 'SILABS':
            self.hardware_platform = BoardType.SiLabs
        else:
            logger.error("Unknown hardware platform")
            assert False

        if config_struct.get("Outputs"):
            self.device_profile_id = config_struct["Outputs"].get("DEVICE_PROFILE_ID")
            self.web_ui_url = config_struct["Outputs"].get("WEB_UI_URL")
        else:
            self.device_profile_id = None
            self.web_ui_url = None

        if config_struct.get("_Paths"):
            self.provision_script_directory = config_struct["_Paths"].get("PROVISION_SCRIPT_DIR", None)
            self.arm_toolchain_dir = config_struct["_Paths"].get("ARM_TOOLCHAIN_DIR", None)
            self.commander_dir = config_struct["_Paths"].get("SILABS_COMMANDER_TOOLS_DIR", None)
        else:
            self.provision_script_directory = None
            self.arm_toolchain_dir = None
            self.commander_dir = None

        self.my_cwd = os.path.dirname(os.path.realpath(__file__))

        logger.debug(f"Loaded configuration: AWS_PROFILE: {self.aws_profile}, DESTINATION: {self.destination_name} , "
                    f"DEVICE_PROFILE: {self.device_profile_id}")

    def update_profile_id(self, device_profile_id):
        self.device_profile_id = device_profile_id
        self.update_cfg_param("DEVICE_PROFILE_ID", self.device_profile_id)

    def update_cfg_param(self, param: str, val: str):
        new_lines = []
        with open(self.config_file, 'r') as config:
            lines = config.readlines()
        for line in lines:
            if param in line:
                comment = '' if '#' not in line else ' #' + line.split('#') - 1.
                new_lines.append(f'    {param}: {val}{comment}\n')
            else:
                new_lines.append(line)
        with open(self.config_file, 'w') as config:
            config.writelines(new_lines)

    def read_config_file(self):
        with open(self.config_file, 'r') as file:
            if self.config_file_type == ".json":
                return json.load(file)
            elif self.config_file_type == ".yaml":
                return yaml.safe_load(file)
            else:
                logger.error("Unrecognized extension of config file")
                assert False

    def write_config_file(self, config_struct):
        with open(self.config_file, "w") as file:
            if self.config_file_type == ".json":
                json.dump(config_struct, file, indent=4)
            elif self.config_file_type == ".yaml":
                yaml.dump(config_struct, file, indent=4)
            else:
                logger.error("Unrecognized extension of config file")
                assert False

