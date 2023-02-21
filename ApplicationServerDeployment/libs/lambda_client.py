# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import base64
from io import BytesIO
from pathlib import Path
from time import sleep

import boto3
from botocore.exceptions import ClientError

from libs.config import Config
from libs.utils import zip_top_level_files, log_info, eval_client_response, terminate, \
    ErrCode, zip_dir


class LambdaClient:
    """
    Provides lambda client with methods necessary to update lambda config and upload lambda code.

    Attributes
    ----------
        _client: botocore.client.lambda
            Lambda client.

    """

    def __init__(self, session: boto3.Session):
        self.lambda_client = session.client(service_name='lambda')

    def upload_lambda_files(self, parent: Path):
        """
        Uploads code to SidewalkUplinkLambda, SidewalkDownlinkLambda and SidewalkDbHandlerLambda
        :param parent: parent path
        """
        lambdas = ['SidewalkUplinkLambda', 'SidewalkDownlinkLambda', 'SidewalkDbHandlerLambda']
        dirs = ['uplink', 'downlink', 'db_handler']
        for idx, (lam, dir) in enumerate(zip(lambdas, dirs)):
            buffer = BytesIO()
            log_info(f'Uploading {lam} files...')
            zip_top_level_files(parent.joinpath('lambda', 'codec'), buffer)
            zip_top_level_files(parent.joinpath('lambda', 'database'), buffer)
            zip_top_level_files(parent.joinpath('lambda', 'utils'), buffer)
            zip_top_level_files(parent.joinpath('lambda', dir), buffer)
            try:
                response = self.lambda_client.update_function_code(FunctionName=lam, ZipFile=buffer.getvalue())
                eval_client_response(response, f'{lam} function updated.')
            except ClientError as e:
                terminate(f'Unable to update lambda: {e}.', ErrCode.EXCEPTION)

    def update_auth_lambda(self, config: Config, parent: Path):
        """
        Uploads code to SidewalkUserAuthenticationLambda, SidewalkApiGwAuthenticationLambda and SidewalkUserRequestTokenSignerLambda.
        Updates lambda code with new credentials
        :param config: credentials are extracted from config
        :param parent: parent path
        """
        auth_lambdas = ['SidewalkUserAuthenticationLambda', 'SidewalkApiGwAuthenticationLambda', 'SidewalkUserRequestTokenSignerLambda' ]
        auth_dirs = ['authUser', 'authApiGw', 'authRequestSigner']
        auth_bytes = f'{config.username}:{config.password}'.encode('ascii')
        auth_string = base64.b64encode(auth_bytes).decode('ascii')
        for idx, (lam, dir) in enumerate(zip(auth_lambdas, auth_dirs)):
            buffer = BytesIO()
            log_info(f'Uploading {lam} files...')
            zip_dir(parent.joinpath('lambda', 'authLibs'), "authLibs" , buffer)
            zip_top_level_files(parent.joinpath('lambda', dir), buffer)
            try:
                response = self.lambda_client.update_function_configuration(FunctionName=lam, Environment={
                    'Variables': {
                        'CREDENTIALS': auth_string
                    }
                })
                eval_client_response(response, f'{lam} function updated.')

                i = 0
                max_i = 5
                while i < max_i: # we need to wait for previous lambda update to be done
                    i += 1
                    try:
                        response = self.lambda_client.update_function_code(FunctionName=lam, ZipFile=buffer.getvalue())
                        eval_client_response(response, f'{lam} function updated.')
                        break
                    except ClientError as e:
                        log_info(f"Waiting for lambda update to be done, try {i} of {max_i}")
                        sleep(1)

            except ClientError as e:
                terminate(f'Unable to update lambda: {e}.', ErrCode.EXCEPTION)