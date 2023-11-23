# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import datetime
import boto3
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class IOTWirelessAPIHandler:
    """
    A class that has all the API calls for wireless API's
    """

    def __init__(self):
        self._session = boto3.Session()
        self._wireless_client = self._session.client(service_name='iotwireless', endpoint_url= 'https://api.gamma.us-east-1.iotwireless.iot.aws.dev')

    def delete_fuota_task(self, fuota_task_id: str):
        return self._wireless_client.delete_fuota_task(
            Id=fuota_task_id
        )