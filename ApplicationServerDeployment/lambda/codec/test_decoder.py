# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Unit tests for command decoder.
"""
import json
import unittest

from command import Command


class TestDecoder(unittest.TestCase):

    # -----------------------------------------------
    # Decode header
    # -----------------------------------------------
    def test_decodeHeader_shouldSucceed(self):
        cmd = Command().decode('40010102020B030C01')
        self.assertEqual(cmd.status_hdr_ind, '0')
        self.assertEqual(cmd.op_code, '10')
        self.assertEqual(cmd.cls, '00')
        self.assertEqual(cmd.id, '010')
        self.assertEqual(cmd.status_code, '')

    def test_decodeHeader_invalidInput(self):
        cmd = Command()
        with self.assertRaises(ValueError):
            cmd.decode(byte_stream='4Z2010102020B030C01')

    # -----------------------------------------------
    # Decode DEMO_APP_CAP_DISCOVERY_NOTIFICATION msg
    # -----------------------------------------------
    def test_decodeCapabilities_Button1_Led2_Sensor1F_LinkBle_shouldSucceed(self):
        cmd = Command().decode('4001014201020B030C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_CAP_DISCOVERY_NOTIFICATION')
        self.assertEqual(decoded['buttons'], [1])
        self.assertEqual(decoded['leds'], [1, 2])
        self.assertEqual(decoded['link_type'], 'BLE')
        self.assertEqual(decoded['sensor'], True)
        self.assertEqual(decoded['sensor_units'], 'FAHRENHEIT')

    def test_decodeCapabilities_Button3_Led4_Sensor1C_LinkFsk_shouldSucceed(self):
        cmd = Command().decode('40C10301020382010203040B010C02')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_CAP_DISCOVERY_NOTIFICATION')
        self.assertEqual(decoded['buttons'], [1, 2, 3])
        self.assertEqual(decoded['leds'], [1, 2, 3, 4])
        self.assertEqual(decoded['link_type'], 'FSK')
        self.assertEqual(decoded['sensor'], True)
        self.assertEqual(decoded['sensor_units'], 'CELSIUS')

    def test_decodeCapabilities_Button5_Led6_Sensor0_LinkLora_shouldSucceed(self):
        cmd = Command().decode('40C1050102030405C2060102030405060B000C04')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_CAP_DISCOVERY_NOTIFICATION')
        self.assertEqual(decoded['buttons'], [1, 2, 3, 4, 5])
        self.assertEqual(decoded['leds'], [1, 2, 3, 4, 5, 6])
        self.assertEqual(decoded['link_type'], 'LORA')
        self.assertEqual(decoded['sensor'], False)

    # ---------------------------------
    # Decode DEMO_APP_ACTION_RESP  msg
    # ---------------------------------
    def test_decodeLedOnResp_id1_gpsTime10_dlLatency1_LinkBle_shouldSucceed(self):
        gps_time = '0000000A'
        dl_latency = '00000001'
        cmd = Command().decode('61090187' + gps_time + '88' + dl_latency + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_on_resp'], [1])
        self.assertEqual(decoded['gps_time'], 10)
        self.assertEqual(decoded['dl_latency'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeLedOnResp_id12_gpsTime100_dlLatency10_LinkFsk_shouldSucceed(self):
        gps_time = '00000064'
        dl_latency = '0000000A'
        cmd = Command().decode('6149010287' + gps_time + '88' + dl_latency + '0C02')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_on_resp'], [1, 2])
        self.assertEqual(decoded['gps_time'], 100)
        self.assertEqual(decoded['dl_latency'], 10)
        self.assertEqual(decoded['link_type'], 'FSK')

    def test_decodeLedOnResp_id123_gpsTime1000_dlLatency100_LinkLora_shouldSucceed(self):
        gps_time = '000003E8'
        dl_latency = '00000064'
        cmd = Command().decode('61C90301020387' + gps_time + '88' + dl_latency + '0C04')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_on_resp'], [1, 2, 3])
        self.assertEqual(decoded['gps_time'], 1000)
        self.assertEqual(decoded['dl_latency'], 100)
        self.assertEqual(decoded['link_type'], 'LORA')

    def test_decodeLedOffResp_id1_gpsTime10_dlLatency1_LinkFsk_shouldSucceed(self):
        gps_time = '0000000A'
        dl_latency = '00000001'
        cmd = Command().decode('610A0187' + gps_time + '88' + dl_latency + '0C02')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_off_resp'], [1])
        self.assertEqual(decoded['gps_time'], 10)
        self.assertEqual(decoded['dl_latency'], 1)
        self.assertEqual(decoded['link_type'], 'FSK')

    def test_decodeLedOffResp_id12_gpsTime100_dlLatency10_LinkBle_shouldSucceed(self):
        gps_time = '00000064'
        dl_latency = '0000000A'
        cmd = Command().decode('614A010287' + gps_time + '88' + dl_latency + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_off_resp'], [1, 2])
        self.assertEqual(decoded['gps_time'], 100)
        self.assertEqual(decoded['dl_latency'], 10)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeLedOffResp_id123_gpsTime1000_dlLatency100_LinkLora_shouldSucceed(self):
        gps_time = '000003E8'
        dl_latency = '00000064'
        cmd = Command().decode('61CA0301020387' + gps_time + '88' + dl_latency + '0C04')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_off_resp'], [1, 2, 3])
        self.assertEqual(decoded['gps_time'], 1000)
        self.assertEqual(decoded['dl_latency'], 100)
        self.assertEqual(decoded['link_type'], 'LORA')

    def test_decodeLedOffResp_id1234_gpsTime10000_dlLatency1000_LinkLora_shouldSucceed(self):
        gps_time = '00002710'
        dl_latency = '000003E8'
        cmd = Command().decode('618A0102030487' + gps_time + '88' + dl_latency + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_RESP')
        self.assertEqual(decoded['led_off_resp'], [1, 2, 3, 4])
        self.assertEqual(decoded['gps_time'], 10000)
        self.assertEqual(decoded['dl_latency'], 1000)
        self.assertEqual(decoded['link_type'], 'BLE')

    # -----------------------------------------
    # Decode DEMO_APP_ACTION_NOTIFICATION  msg
    # -----------------------------------------
    def test_decodeButtonPress_id1_gpsTime1_LinkBle_shouldSucceed(self):
        gps_time = '00000001'
        cmd = Command().decode('41050187' + gps_time + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['button_press'], [1])
        self.assertEqual(decoded['gps_time'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeButtonPress_id12_gpsTime10_LinkLora_shouldSucceed(self):
        gps_time = '0000000A'
        cmd = Command().decode('4145010287' + gps_time + '0C04')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['button_press'], [1, 2])
        self.assertEqual(decoded['gps_time'], 10)
        self.assertEqual(decoded['link_type'], 'LORA')

    def test_decodeButtonPress_id123_gpsTime100_LinkFsk_shouldSucceed(self):
        gps_time = '00000064'
        cmd = Command().decode('41C50301020387' + gps_time + '0C02')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['button_press'], [1, 2, 3])
        self.assertEqual(decoded['gps_time'], 100)
        self.assertEqual(decoded['link_type'], 'FSK')

    def test_decodeButtonPress_id1234_gpsTime1000_LinkLora_shouldSucceed(self):
        gps_time = '000003E8'
        cmd = Command().decode('41850102030487' + gps_time + '0C04')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['button_press'], [1, 2, 3, 4])
        self.assertEqual(decoded['gps_time'], 1000)
        self.assertEqual(decoded['link_type'], 'LORA')

    def test_decodeSensorData_1B_gpsTime1_LinkBle_shouldSucceed(self):
        gps_time = '00000001'
        cmd = Command().decode('41060187' + gps_time + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['sensor_data'], 1)
        self.assertEqual(decoded['gps_time'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeSensorData_2B_gpsTime1_LinkBle_shouldSucceed(self):
        gps_time = '00000001'
        cmd = Command().decode('4146010287' + gps_time + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['sensor_data'], 258)
        self.assertEqual(decoded['gps_time'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeSensorData_3B_gpsTime1_LinkBle_shouldSucceed(self):
        gps_time = '00000001'
        cmd = Command().decode('41C60301020387' + gps_time + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['sensor_data'], 66051)
        self.assertEqual(decoded['gps_time'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')

    def test_decodeSensorData_4B_gpsTime1_LinkBle_shouldSucceed(self):
        gps_time = '00000001'
        cmd = Command().decode('41860102030487' + gps_time + '0C01')
        cmd_json = json.loads(cmd.__str__())
        decoded = cmd_json['decoded']
        self.assertEqual(cmd_json['id'], 'DEMO_APP_ACTION_NOTIFICATION')
        self.assertEqual(decoded['sensor_data'], 16909060)
        self.assertEqual(decoded['gps_time'], 1)
        self.assertEqual(decoded['link_type'], 'BLE')


if __name__ == '__main__':
    unittest.main()
