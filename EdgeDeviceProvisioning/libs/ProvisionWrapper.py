# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import os
import subprocess
import sys
from enum import Enum

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class BoardType(Enum):
    Nordic = 0,
    TI = 1,
    SiLabs = 2,
    All = 99


class InputType(Enum):
    CERTIFICATE_JSON = 0,
    AWS_API_JSONS = 1


class ProvisionWrapperException(Exception):
    pass

class ProvisionWrapper:
    def __init__(self, script_dir, silabs_commander_dir=None, hardware_platform=BoardType.All):
        self.main_path = os.path.abspath(script_dir)
        self.hardware_platform = hardware_platform

        if silabs_commander_dir:
            self.commander = os.path.abspath(os.path.join(silabs_commander_dir, "commander"))
        else:
            # In not provided, assumed that ARM tools are in PATH
            self.commander = "commander"

        self.SILABS_XG21 = 'mg21'
        self.SILABS_XG24 = 'mg24'
        self.SILABS_XG21_MEMORY = '1024'
        self.SILABS_XG24_MEMORY = '1536'

    def generate_mfg(self, output_dir, input_type, wireless_device_path=None, device_profile_path=None,
                     certificate_json=None):
        if input_type == InputType.CERTIFICATE_JSON:
            assert certificate_json, "For selected provisioning method, certificate_json is mandatory!"
            assert os.path.exists(certificate_json), f"File not found: {certificate_json}"
        elif input_type == InputType.AWS_API_JSONS:
            assert wireless_device_path, "For selected provisioning method, wireless device json is mandatory"
            assert device_profile_path, "For selected provisioning method, device_profile is mandatory"
            assert os.path.exists(wireless_device_path), f"File not found: {wireless_device_path}"
            assert os.path.exists(device_profile_path), f"File not found: {device_profile_path}"
        else:
            assert False, "Unknown provisioning method"

        board = self.hardware_platform

        if board == BoardType.Nordic or board == BoardType.All:
            logger.info("  Generating MFG.hex for Nordic")
            nordic_bin = os.path.join(output_dir, "Nordic_MFG.bin")
            nordic_hex = os.path.join(output_dir, "Nordic_MFG.hex")
            if input_type == InputType.AWS_API_JSONS:
                self.generate_bin_and_hex_from_aws_jsons(device_json=wireless_device_path,
                                                         profile_json=device_profile_path,
                                                         board=BoardType.Nordic,
                                                         out_bin=nordic_bin,
                                                         chip="nrf52840",
                                                         out_hex=nordic_hex)
            else:
                self.generate_bin_and_hex_from_certificate_json(certificate=certificate_json,
                                                                board=BoardType.Nordic,
                                                                out_bin=nordic_bin,
                                                                chip="nrf52840",
                                                                out_hex=nordic_hex)

        if board == BoardType.TI or board == BoardType.All:
            logger.info("  Generating MFG.hex for TI P1 and TI P7")
            ti_bin = os.path.join(output_dir, "TI.bin")
            ti_p1_hex = os.path.join(output_dir, "TI_P1_MFG.hex")
            ti_p7_hex = os.path.join(output_dir, "TI_P7_MFG.hex")
            if input_type == InputType.AWS_API_JSONS:
                self.generate_bin_and_hex_from_aws_jsons(device_json=wireless_device_path,
                                                         profile_json=device_profile_path,
                                                         board=BoardType.TI,
                                                         out_bin=ti_bin,
                                                         chip="P1",
                                                         out_hex=ti_p1_hex)
                self.generate_bin_and_hex_from_aws_jsons(device_json=wireless_device_path,
                                                         profile_json=device_profile_path,
                                                         board=BoardType.TI,
                                                         out_bin=ti_bin,
                                                         chip="P7",
                                                         out_hex=ti_p7_hex)
            else:
                self.generate_bin_and_hex_from_certificate_json(certificate=certificate_json,
                                                                board=BoardType.TI,
                                                                out_bin=ti_bin,
                                                                chip="P1",
                                                                out_hex=ti_p1_hex)
                self.generate_bin_and_hex_from_certificate_json(certificate=certificate_json,
                                                                board=BoardType.TI,
                                                                out_bin=ti_bin,
                                                                chip="P7",
                                                                out_hex=ti_p7_hex)

        if board == BoardType.SiLabs or board == BoardType.All:
            logger.info("  Generating MFG.S37 For SiLabs xG21 and xG24")
            sl_mfg_nvm3 = os.path.join(output_dir, "SiLabs_MFG.nvm3")
            sl_xg21_mfg_s37 = os.path.join(output_dir, 'Silabs_xG21.s37')
            sl_xg24_mfg_s37 = os.path.join(output_dir, 'Silabs_xG24.s37')
            if input_type == InputType.AWS_API_JSONS:
                self.generate_nvm3_and_s37_from_aws_jsons(device_json=wireless_device_path,
                                                          profile_json=device_profile_path,
                                                          board=BoardType.SiLabs,
                                                          out_nvm3=sl_mfg_nvm3,
                                                          chip=self.SILABS_XG21,
                                                          memory=self.SILABS_XG21_MEMORY,
                                                          outfile_s37=sl_xg21_mfg_s37)
                self.generate_nvm3_and_s37_from_aws_jsons(device_json=wireless_device_path,
                                                          profile_json=device_profile_path,
                                                          board=BoardType.SiLabs,
                                                          out_nvm3=sl_mfg_nvm3,
                                                          chip=self.SILABS_XG24,
                                                          memory=self.SILABS_XG24_MEMORY,
                                                          outfile_s37=sl_xg24_mfg_s37)

            else:
                self.generate_nvm3_and_s37_from_certificate_json(certificate=certificate_json,
                                                                 board=BoardType.SiLabs,
                                                                 out_nvm3=sl_mfg_nvm3,
                                                                 chip=self.SILABS_XG21,
                                                                 memory=self.SILABS_XG21_MEMORY,
                                                                 outfile_s37=sl_xg21_mfg_s37)

                self.generate_nvm3_and_s37_from_certificate_json(certificate=certificate_json,
                                                                 board=BoardType.SiLabs,
                                                                 out_nvm3=sl_mfg_nvm3,
                                                                 chip=self.SILABS_XG24,
                                                                 memory=self.SILABS_XG24_MEMORY,
                                                                 outfile_s37=sl_xg24_mfg_s37)

    def generate_bin_and_hex_from_aws_jsons(self, device_json, profile_json, board, out_bin, chip, out_hex):
        assert board in (BoardType.Nordic, BoardType.TI), "Operation supported only for Nordic and TI"

        platform = "ti" if board == BoardType.TI else "nordic"

        result = subprocess.run(args=[sys.executable, 'provision.py', platform, 'aws', '--wireless_device_json', device_json,
                                      '--device_profile_json', profile_json,
                                      '--output_bin', out_bin, '--chip', chip, '--output_hex', out_hex],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_nvm3_and_s37_from_aws_jsons(self, device_json, profile_json, board, out_nvm3, chip, memory, outfile_s37):
        assert board == BoardType.SiLabs, "Operation supported only for SiLabs"
        args=[sys.executable, 'provision.py', 'silabs', 'aws', '--wireless_device_json', device_json,
                                      '--device_profile_json', profile_json,
                                      '--output_nvm3', out_nvm3,
                                      '--chip', chip, '--memory', memory, '--output_s37', outfile_s37]
        result = subprocess.run(args=args,
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_bin_and_hex_from_certificate_json(self, certificate, board, out_bin, chip, out_hex):
        assert board in (BoardType.Nordic, BoardType.TI), "Operation supported only for Nordic and TI"

        platform = "ti" if board == BoardType.TI else "nordic"

        result = subprocess.run(args=[sys.executable, 'provision.py', platform, 'aws', '--certificate_json', certificate,
                                      '--output_bin', out_bin, '--chip', chip, '--output_hex', out_hex],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_nvm3_and_s37_from_certificate_json(self, certificate, board, out_nvm3, chip, memory, outfile_s37):
        assert board == BoardType.SiLabs, "Operation supported only for SiLabs"
        args = [sys.executable, 'provision.py', 'silabs', 'aws', '--certificate_json', certificate,
                                      '--output_nvm3', out_nvm3, '--chip', chip, '--memory', memory, '--output_s37', outfile_s37]
        result = subprocess.run(args=args,
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")


def print_subprocess_results(result, subprocess_name="", withAssert=True):
    if result.returncode != 0:
        message = " ".join(result.args)
        message += " \n"
        message += " " + result.stdout.decode()
        message += " " + result.stderr.decode()
        raise ProvisionWrapperException(message)

    for line in result.stdout.decode().splitlines():
        logger.debug(line)
        if withAssert:
            assert 'error' not in line, f"Something went wrong after calling subprocess {subprocess_name}"

    for line in result.stderr.decode().splitlines():
        logger.error(line)
        if withAssert:
            assert 'error' not in line, f"Something went wrong after calling subprocess {subprocess_name}"
