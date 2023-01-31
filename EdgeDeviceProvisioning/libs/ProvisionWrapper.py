# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import logging
import os
import subprocess
import sys
from enum import Enum
from intelhex import bin2hex

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


class ProvisionWrapper:
    def __init__(self, script_dir, arm_toolchain_dir=None, silabs_commander_dir=None, hardware_platform=BoardType.All):
        self.main_path = os.path.abspath(script_dir)
        self.provision_cfg_nordic = os.path.join('config', 'nordic', 'nrf528xx_dk', 'config.yaml')
        self.provision_cfg_ti = os.path.join('config', 'ti', 'cc13x2_26x2', 'config.yaml')
        self.hardware_platform = hardware_platform

        if silabs_commander_dir:
            self.commander = os.path.abspath(os.path.join(silabs_commander_dir, "commander"))
        else:
            # In not provided, assumed that ARM tools are in PATH
            self.commander = "commander"

        self.NORDIC_ADDR = '0xFD000'
        self.TI_P1_ADDR = '0x56000'
        self.TI_P7_ADDR = '0xAE000'
        self.SILABS_XG21_ADDR = '0x000F2000'
        self.SILABS_XG24_ADDR = '0x08172000'
        self.SILABS_XG21_DEVICE = 'EFR32MG21A020F1024IM32'
        self.SILABS_XG24_DEVICE = 'EFR32MG24A020F1536GM48'

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
                self.generate_bin_from_aws_jsons(wireless_device_path, device_profile_path, BoardType.Nordic,
                                                 nordic_bin)
            else:
                self.generate_bin_from_certificate_json(certificate_json, BoardType.Nordic, nordic_bin)
            self.generate_hex_with_intelhex(nordic_bin, nordic_hex, self.NORDIC_ADDR)

        if board == BoardType.TI or board == BoardType.All:
            logger.info("  Generating MFG.hex for TI P1 and TI P7")
            ti_bin = os.path.join(output_dir, "TI.bin")
            ti_p1_hex = os.path.join(output_dir, "TI_P1_MFG.hex")
            ti_p7_hex = os.path.join(output_dir, "TI_P7_MFG.hex")
            if input_type == InputType.AWS_API_JSONS:
                self.generate_bin_from_aws_jsons(wireless_device_path, device_profile_path, BoardType.TI, ti_bin)
            else:
                self.generate_bin_from_certificate_json(certificate_json, BoardType.TI, ti_bin)
            self.generate_hex_with_intelhex(ti_bin, ti_p1_hex, self.TI_P1_ADDR)
            self.generate_hex_with_intelhex(ti_bin, ti_p7_hex, self.TI_P7_ADDR)

        if board == BoardType.SiLabs or board == BoardType.All:
            logger.info("  Generating MFG.S37 For SiLabs xG21 and xG24")
            sl_mfg_nvm3 = os.path.join(output_dir, "SiLabs_MFG.nvm3")
            sl_xg21_mfg_s37 = os.path.join(output_dir, 'Silabs_xG21.s37')
            sl_xg24_mfg_s37 = os.path.join(output_dir, 'Silabs_xG24.s37')
            if input_type == InputType.AWS_API_JSONS:
                self.generate_nvm3_from_aws_jsons(wireless_device_path, device_profile_path, BoardType.SiLabs, sl_mfg_nvm3)
            else:
                self.generate_nvm3_from_certificate_json(certificate_json, BoardType.SiLabs, sl_mfg_nvm3)
            self.generate_s37_with_silabs_commander(sl_mfg_nvm3, self.SILABS_XG21_ADDR, self.SILABS_XG21_DEVICE,
                                                    sl_xg21_mfg_s37)
            self.generate_s37_with_silabs_commander(sl_mfg_nvm3, self.SILABS_XG24_ADDR, self.SILABS_XG24_DEVICE,
                                                    sl_xg24_mfg_s37)

    def generate_bin_from_aws_jsons(self, device_json, profile_json, board, out_bin):
        assert board in (BoardType.Nordic, BoardType.TI), "Operation supported only for Nordic and TI"
        provision_cfg = self.provision_cfg_nordic
        if board == BoardType.TI:
            provision_cfg = self.provision_cfg_ti

        result = subprocess.run(args=[sys.executable, 'provision.py', 'aws', '--wireless_device_json', device_json,
                                      '--device_profile_json', profile_json,
                                      '--output_bin', out_bin, '--config', provision_cfg],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_nvm3_from_aws_jsons(self, device_json, profile_json, board, out_nvm3):
        assert board == BoardType.SiLabs, "Operation supported only for SiLabs"
        result = subprocess.run(args=[sys.executable, 'provision.py', 'aws', '--wireless_device_json', device_json,
                                      '--device_profile_json', profile_json,
                                      '--output_sl_nvm3', out_nvm3],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_bin_from_certificate_json(self, certificate, board, out_bin):
        assert board in (BoardType.Nordic, BoardType.TI), "Operation supported only for Nordic and TI"
        provision_cfg = self.provision_cfg_nordic
        if board == BoardType.TI:
            provision_cfg = self.provision_cfg_ti

        result = subprocess.run(args=[sys.executable, 'provision.py', 'aws', '--certificate_json', certificate,
                                      '--output_bin', out_bin, '--config', provision_cfg],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_nvm3_from_certificate_json(self, certificate, board, out_nvm3):
        assert board == BoardType.SiLabs, "Operation supported only for SiLabs"
        result = subprocess.run(args=[sys.executable, 'provision.py', 'aws', '--certificate_json', certificate,
                                      '--output_sl_nvm3', out_nvm3],
                                cwd=self.main_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name="provision.py")

    def generate_hex_with_intelhex(self, bin, hex, address):
        result = bin2hex(fin=bin, fout=hex, offset=int(address, base=16))
        assert result == 0, f"Converting {bin} to {hex} failed"

    def generate_s37_with_silabs_commander(self, nvm3_file, address, device, outfile_s37):
        # S37 initfile
        temp_initfile = outfile_s37+"_initfile.s37"
        result = subprocess.run(args=[self.commander, 'nvm3', 'initfile', 
                                      '--address', f'{address}',
                                      '--size', '0x6000',
                                      '--device', f'{device}',
                                      '--outfile', f'{temp_initfile}'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name=self.commander)
        
        # S37 MFG
        result = subprocess.run(args=[self.commander, 'nvm3', 'set', temp_initfile,
                                     '--nvm3file', nvm3_file, 
                                     '--outfile', outfile_s37], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_subprocess_results(result, subprocess_name=self.commander)
        
        os.remove(temp_initfile)


def print_subprocess_results(result, subprocess_name="", withAssert=True):
    for line in result.stdout.decode().splitlines():
        logger.debug(line)
        if withAssert:
            assert 'error' not in line, f"Something went wrong after calling subprocess {subprocess_name}"

    for line in result.stderr.decode().splitlines():
        logger.error(line)
        if withAssert:
            assert 'error' not in line, f"Something went wrong after calling subprocess {subprocess_name}"
