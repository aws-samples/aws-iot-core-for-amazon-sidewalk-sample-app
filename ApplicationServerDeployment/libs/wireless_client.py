# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from botocore.exceptions import ClientError

from libs.utils import *


class WirelessClient:
    """
    Provides WirelessClient client with methods necessary handle Sidewalk destination and wireless events configuration.

    Attributes
    ----------
        _wireless_client: botocore.client.IoTWireless
            Client to IoTWireless.
        _iam_client: botocore.client.IAM
            Client to AWS IAM.

    """

    def __init__(self, session: boto3.Session):
        self._wireless_client = session.client(service_name='iotwireless')
        self._iam_client = session.client(service_name='iam')

    # -------
    # Deploy
    # -------
    def check_if_destination_exists(self, name: str) -> bool:
        """
        Checks if given destination already exists.

        :param name:    Destination name.
        :return:        True if exists, False otherwise.
        """
        try:
            log_info(f'Checking if {name} destination exists...')
            response = self._wireless_client.get_destination(Name=name)
            eval_client_response(
                response,
                f'{name} already exists and will not be included in the SidewalkSampleApplicationStack.'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                log_success(f'{name} does not exist and will be included in the SidewalkSampleApplicationStack.')
                return False
            else:
                terminate(f'Unable to get {name} destination: {e}.', ErrCode.EXCEPTION)

    def update_existing_destination(self, dest_name: str, role_name: str):
        """
        Updates existing destination for uplink messages from Sidewalk devices.

        :param dest_name:   Destination name.
        :param role_name:   Name of the role to be assigned to the destination.
        """
        log_info(f'{dest_name} already exists and will be modified. Proceed?')
        confirm()
        try:
            log_info(f'Getting {role_name} role ARN...')
            response = self._iam_client.get_role(RoleName=f'{role_name}')
            log_success(f'{role_name} ARN obtained.')
            log_info(f'Updating {dest_name} destination...')
            role_arn = response['Role']['Arn']
            response = self._wireless_client.update_destination(
                Name=dest_name,
                ExpressionType='MqttTopic',
                Expression='sidewalk/app_data',
                Description='Destination for uplink messages from Sidewalk devices.',
                RoleArn=role_arn
            )
            eval_client_response(response, f'{dest_name} role updated.')
        except ClientError as e:
            terminate(f'Unable to update {dest_name} destination: {e}.', ErrCode.EXCEPTION)

    def enable_notifications(self):
        """
        Enables notifications for Sidewalk devices
        """
        try:
            log_info('Enabling Sidewalk event notification in iotwireless...')
            response = self._wireless_client.update_event_configuration_by_resource_types(
                DeviceRegistrationState={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}},
                Proximity={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}},
                MessageDeliveryStatus={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}}
            )
            eval_client_response(response, 'Notifications enabled.')
        except ClientError as e:
            terminate(f'Notifications not enabled: {e}.', ErrCode.EXCEPTION)
