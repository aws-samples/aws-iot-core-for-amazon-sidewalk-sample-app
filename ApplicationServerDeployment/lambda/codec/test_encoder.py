# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Unit tests for command decoder.
"""
import unittest

from command import Command
from protocol import *
from tag import Tag


class TestEncoder(unittest.TestCase):

    # -----------------------------------------------
    # Invalid params
    # -----------------------------------------------
    def test_encodeHeader_invalidHeader(self):
        with self.assertRaises(AttributeError):
            Command().encode(
                status_hdr_ind=True,
                op_code=OpCode.MSG_TYPE_RESP,
                cls=True,
                id=Id.DEMO_APP_ACTION_RESP,
                status_code='00000000',
                payload=[]
            )

    def test_encodeHeader_invalidPayload(self):
        tags_json = [{'NonExistentTag': '1'}]
        with self.assertRaises(ValueError):
            [Tag().encode(tag) for tag in tags_json]

    # ----------------------------------------
    # Encode DEMO_APP_CAP_DISCOVERY_RESP  msg
    # ----------------------------------------
    def test_encodeDemoAppCapDiscoveryResp_shouldSucceed(self):
        status_code = '00000000'
        cmd = Command()
        self.assertEqual(cmd.hex_repr(), '')
        cmd.encode(
            status_hdr_ind=True,
            op_code=OpCode.MSG_TYPE_RESP,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_CAP_DISCOVERY_RESP,
            status_code=status_code
        )
        self.assertEqual(cmd.hex_repr(), 'E000')

    # --------------------------------
    # Encode DEMO_APP_ACTION_RESP msg
    # --------------------------------
    def test_encodeButtonPressedResp_id1_shouldSucceed(self):
        tags_json = [{TagType.BUTTON_PRESSED_RESP: [1]}]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=True,
            op_code=OpCode.MSG_TYPE_RESP,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_RESP,
            status_code='00000000',
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), 'E1000D01')

    def test_encodeButtonPressedResp_id24_shouldSucceed(self):
        tags_json = [{TagType.BUTTON_PRESSED_RESP: [2, 4]}]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=True,
            op_code=OpCode.MSG_TYPE_RESP,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_RESP,
            status_code='00000000',
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), 'E1004D0204')

    def test_encodeButtonPressedResp_id124_shouldSucceed(self):
        tags_json = [{TagType.BUTTON_PRESSED_RESP: [1, 2, 4]}]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=True,
            op_code=OpCode.MSG_TYPE_RESP,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_RESP,
            status_code='00000000',
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), 'E100CD03010204')

    # -------------------------------
    # Encode DEMO_APP_ACTION_REQ msg
    # -------------------------------
    def test_encodeLedOn_id1_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_ON: [1]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21030187000003E8')

    def test_encodeLedOn_id12_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_ON: [1, 2]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '2143010287000003E8')

    def test_encodeLedOn_id123_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_ON: [1, 2, 3]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21C30301020387000003E8')

    def test_encodeLedOn_id1234_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_ON: [1, 2, 3, 4]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21830102030487000003E8')

    def test_encodeLedOff_id1_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_OFF: [1]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21040187000003E8')

    def test_encodeLedOff_id12_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_OFF: [1, 2]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '2144010287000003E8')

    def test_encodeLedOff_id123_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_OFF: [1, 2, 3]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21C40301020387000003E8')

    def test_encodeLedOff_id1234_gpsTime1000_shouldSucceed(self):
        tags_json = [
            {TagType.LED_OFF: [1, 2, 3, 4]},
            {TagType.CURRENT_GPS_TIME_IN_SECS: 1000}
        ]
        tags = [Tag().encode(tag) for tag in tags_json]
        cmd = Command().encode(
            status_hdr_ind=False,
            op_code=OpCode.MSG_TYPE_WRITE,
            cls=Class.DEMO_APP_CLASS,
            id=Id.DEMO_APP_ACTION_REQ,
            payload=tags
        )
        self.assertEqual(cmd.hex_repr(), '21840102030487000003E8')


if __name__ == '__main__':
    unittest.main()
