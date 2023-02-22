# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from io import BytesIO
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from time import sleep

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

    def upload_lambda_files(self, parent: Path, lambdas: [str], dirs: [str], library_dirs: [str] = None):
        """
        Uploads code to lambda.
        :param library_dirs: directories which will be used in each lambda lambda as library.
         It means that they will keep its tree structure.
        :param dirs: directories with lambda code
        :param lambdas: list of lambda names to update
        :param parent: parent path
        """
        for idx, (lam, dir) in enumerate(zip(lambdas, dirs)):
            buffer = BytesIO()
            log_info(f'Uploading {lam} files...')
            if library_dirs is not None:
                for library in library_dirs:
                    zip_dir(parent.joinpath('lambda', library), library, buffer)
            zip_top_level_files(parent.joinpath('lambda', dir), buffer)
            try:
                response = self.lambda_client.update_function_code(FunctionName=lam, ZipFile=buffer.getvalue())
                eval_client_response(response, f'{lam} function updated.')
            except ClientError as e:
                terminate(f'Unable to update lambda: {e}.', ErrCode.EXCEPTION)

    def update_lambda_env_variables(self, lambdas: [str], env_variables: dict):
        """
        Updates lambda environment variables. Includes retry mechanism.
        :param env_variables: dict[str, str] where keys are env_variable keys and values are env_variable values
        :param lambdas: list of lambda names to update
        """
        for lam in lambdas:
            retries = 0
            log_info(f'Updating {lam} environment variables...')
            while True:
                try:
                    response = self.lambda_client.update_function_configuration(FunctionName=lam, Environment={
                            'Variables': env_variables
                    })
                    eval_client_response(response, f'Environment variables updated.')
                    break
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceConflictException' and retries < 5:
                        retries += 1
                        sleep(1)
                    else:
                        terminate(f'Unable to update environment variables: {e}', ErrCode.EXCEPTION)
