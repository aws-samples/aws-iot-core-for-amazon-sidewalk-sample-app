# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Class for encoding/decoding Sidewalk Sensor Monitoring Demo Application commands.
"""
import json

from protocol import *
from tag import Tag


class Command:
    """
    A class representing Sidewalk Sensor Monitoring Demo Application command.
    May be used to:
     - decode hexadecimal byte_stream into the command (for UL messages)
     - encode command into hexadecimal byte_stream (for DL messages)

    Attributes
    ----------
        status_hdr_ind: str
            Binary string representing status header indicator.
        op_code: str
            Binary string representing operation code.
        cls: str
            Binary string representing command class.
        id: str
            Binary string representing command id.
        status_code: str
            Binary string representing status_code.
        raw_payload: str
            Binary string representing raw_payload (not interpreted sequence of TLVs).
        payload: [Tag]
            List of Tag objects.
    """
    def __init__(self):
        self.status_hdr_ind = ''
        self.op_code = ''
        self.cls = ''
        self.id = ''
        self.status_code = ''
        self.raw_payload = ''
        self.payload = []
        self.decoded_cmd = {}

    def decode(self, byte_stream):
        """
        Decodes byte_stream into human-readable representation of the command.

        :param byte_stream:     Hexadecimal byte stream.
        :return:                Command object.
        """
        raw_cmd = Command.hex_to_bin(byte_stream)

        # decode binary stream
        status_hdr_ind_bool = True if raw_cmd[0] == '1' else False
        self.status_hdr_ind = raw_cmd[0]
        self.op_code = raw_cmd[1:2 + 1]
        self.cls = raw_cmd[3:4 + 1]
        self.id = bin((int(raw_cmd[5:7 + 1], 2) << 2) | int(self.op_code, 2))[2:]
        padding = 3 - len(self.id)
        if padding:
            self.id = padding * '0' + self.id
        self.status_code = raw_cmd[8:16] if status_hdr_ind_bool else ''
        self.raw_payload = raw_cmd[16:] if status_hdr_ind_bool else raw_cmd[8:]
        self.payload = []
        try:
            if len(self.raw_payload) > 0:
                extract = Command.extract_tags(self.raw_payload)
                while True:
                    self.payload.append((next(extract)))
        except StopIteration:
            pass

        # create human-readable dict
        self.decoded_cmd = self.combine_tags(self.payload)
        self.decoded_cmd['id'] = Id(self.id).name

        return self

    def encode(self, status_hdr_ind: bool, op_code: OpCode, cls: Class, id: Id, status_code: str = '', payload: [Tag] = None):
        """
        Encodes arguments into byte_stream.

        :param status_hdr_ind:  Is status header included (bool).
        :param op_code:         OpCode enum.
        :param cls:             Class enum.
        :param id:              Id enum.
        :param status_code:     Status code str.
        :param payload:         List of Tag objects.
        :return:                Command object.
        """
        self.status_hdr_ind = '1' if status_hdr_ind else '0'
        self.op_code = op_code.value
        self.cls = cls.value
        self.id = id.value
        self.status_code = status_code
        payload = payload or []
        self.payload = payload
        self.raw_payload = ''.join([tag.bin_repr() for tag in payload])
        self.decoded_cmd = self.combine_tags(self.payload)
        self.decoded_cmd['id'] = Id(self.id).name

        return self

    def bin_repr(self, separate_bytes=False):
        """
        Returns binary representation of the command.
        :param separate_bytes:  If true, inserts space, which separates bytes.
        :return:                Binary string.
        """
        cmd_id = '' if self.id == '' else IdToCmdIdValueMap[Id(self.id)]
        bin_str = self.status_hdr_ind + self.op_code + self.cls + cmd_id + self.status_code + self.raw_payload
        if separate_bytes:
            bin_str = ' '.join(bin_str[i:i + 8] for i in range(0, len(bin_str), 8))
        return bin_str

    def hex_repr(self):
        """
        Returns hexadecimal representation of the command.
        :return:    Hexadecimal string.
        """
        try:
            return Command.bin_to_hex(self.bin_repr()).upper()
        except ValueError:
            return ''

    def json_repr(self):
        """
        Returns json representation of the command.
        :return:    Human-readable json.
        """
        return json.dumps(self.decoded_cmd)

    def __repr__(self):
        bin_str = self.bin_repr()
        return f'Command(\'{Command.bin_to_hex(bin_str)}\')'

    def __str__(self):
        payload = [(tag.dict_repr()) for tag in self.payload]
        command = {
            'status_hdr_indicator': True if self.status_hdr_ind == '1' else False,
            'op-code': OpCode(self.op_code).name,
            'class': Class(self.cls).name,
            'id': Id(self.id).name,
            'status_code': self.status_code,
            'payload': payload,
            'decoded': self.decoded_cmd
        }
        return json.dumps(command)

    @staticmethod
    def hex_to_bin(hex_str: str) -> str:
        """
        Coverts hexadecimal string into its binary representation.
        :param hex_str:     Hexadecimal string.
        :return:            Binary string.
        """
        bin_str = bin(int(hex_str, 16))[2:]
        padding = (4 - (len(bin_str) % 4)) % 4
        return '0' * padding + bin_str

    @staticmethod
    def bin_to_hex(bin_str: str) -> str:
        """
        Coverts binary string into its hexadecimal representation.
        :param bin_str: Binary String.
        :return:        Hexadecimal string.
        """
        return hex(int(bin_str, 2))[2:]

    @staticmethod
    def extract_tags(bin_payload: str) -> Tag:
        """
        Generator, which extracts tags from the given binary string, one by one.
        :param bin_payload:     Binary string, which represents payload.
        :return:                Generator, which produces Tag objects.
        """
        exhausted = False
        while not exhausted:
            format = bin_payload[0:1 + 1]
            type = bin_payload[2:7 + 1]
            frmt = TlvFormat(format)

            if frmt == TlvFormat.STANDARD:
                # 11 (STANDARD) | 6b key | 1B len | val
                val_len = bin_payload[8:15 + 1]
                length = int(val_len, 2)
                val_start_idx = 16
            else:
                # __ (SIZE_OPTIMIZED) | 6b key | val
                val_len = ''
                if frmt == TlvFormat.SIZE_OPTIMIZED_4B:
                    length = 4
                else:
                    length = int(frmt.value, 2) + 1
                val_start_idx = 8

            val_end_idx = val_start_idx + length * 8
            val = bin_payload[val_start_idx:val_end_idx]
            bin_payload = bin_payload[val_end_idx:]

            if not bin_payload:
                exhausted = True

            tag = Tag()
            tag.decode(type, format, val, val_len)
            yield tag

    @staticmethod
    def combine_tags(payload: [Tag]) -> str:
        """
        Combines tags into single, human-readable dict.
        :param payload:     List of Tag objects.
        :return:            Dict combining all provided tags.
        """
        dicts = [tag.json for tag in payload]
        return {key: val for d in dicts for key, val in d.items()}
