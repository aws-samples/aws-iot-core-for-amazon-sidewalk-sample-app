# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3

from botocore.exceptions import ClientError
from libs.utils import log_info, log_success, terminate, ErrCode


class CloudFrontClient:
    """
    Provides CloudFront client with methods necessary to disable distributions.

    Attributes
    ----------
        _client: botocore.client.cloudfront
            Client to cloudfront.

    """

    def __init__(self, session: boto3.Session):
        self._client = session.client(service_name='cloudfront')

    def disable_distribution(self, distribution_id: str):
        """
        Disables distribution
        :param distribution_id: id of distribution
        """
        try:
            print(f'gettin distribution {distribution_id}')
            config: dict = self._client.get_distribution_config(Id=distribution_id)
            dist_config: dict = config.get("DistributionConfig")
            dist_config["Enabled"] = False
            self._client.update_distribution(DistributionConfig=dist_config, IfMatch=config.get("ETag"), Id=distribution_id)
        except ClientError as e:
            terminate(f'Unable to disable distribution: {e}.', ErrCode.EXCEPTION)