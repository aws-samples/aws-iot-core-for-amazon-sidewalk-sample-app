# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import boto3

from botocore.exceptions import ClientError
from io import BytesIO
from pathlib import Path
from libs.utils import log_info, log_success, terminate, ErrCode


class S3Client:
    """
    Provides S3 client with methods necessary to delete bucket contents.

    Attributes
    ----------
        _client: botocore.client.s3
            Client to s3.

    """

    def __init__(self, session: boto3.Session):
        self._client = session.client(service_name='s3')
        self.region_name = session.region_name

    def delete_bucket_content(self, bucket_name):
        """
        Deletes contents of buckets
        :param bucket_name: name of bucket to clear
        """
        try:
            log_info(f'Deleting objects from {bucket_name} bucket...')
            paginator = self._client.get_paginator("list_objects_v2")
            results = paginator.paginate(Bucket=bucket_name).build_full_result().get("Contents", None)
            object_names = []
            if results is not None:
                for obj in results:
                    obj_dict = {"Key": obj["Key"]}
                    object_names.append(obj_dict)
            if len(object_names) > 0:
                self._client.delete_objects(Bucket=bucket_name,
                                            Delete={"Objects": object_names})
            log_success('Objects deleted, bucket is empty.')
        except ClientError as e:
            if e.response['Error']['Code'] in ['ValidationError', 'NoSuchBucket']:
                log_success(f'{bucket_name} doesn\'t exist, skipping.')
            else:
                terminate(f'Unable to delete objects from the bucket: {e}.', ErrCode.EXCEPTION)

    def put_files(self, bucket_name, api_gw_id, build_dir):
        """
        Puts content of web application to s3 bucket
        :param bucket_name: name of s3 bucket
        :param api_gw_id: id of api gateway they will be used for execution of backend requests
        :param build_dir: path to gui directory. Needs to be provided to provide compatibility with mac build
        (it takes parent as lib)
        """
        api_gw_invoke_url = f'https://{api_gw_id}.execute-api.{self.region_name}.amazonaws.com/dev'
        web_app = 'SensorMonitoringApp'

        try:
            self.delete_bucket_content(bucket_name)
            log_info(f'Uploading {web_app} files to the S3 bucket...')
            suffix_map = {
                '.svg': 'image/svg+xml',
                '.png': 'image/png',
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.html': 'text/html'
            }
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    if root == str(build_dir):
                        key = file
                    else:
                        key = Path(root).stem + '/' + file
                    file_path = Path(root, file)
                    if file_path.stem.startswith('index') and file_path.suffix == '.js':
                        with open(file_path, 'r') as fd:
                            # override template: replace <api_gw_invoke_url> placeholder with actual value
                            content = fd.read().replace('<api_gw_invoke_url>', api_gw_invoke_url)
                            data = BytesIO(bytes(content, 'utf-8'))
                            self._client.put_object(Bucket=bucket_name, Key=key, Body=data, ContentType=suffix_map[file_path.suffix])
                    else:
                        with open(file_path, 'rb') as data:
                            self._client.put_object(Bucket=bucket_name, Key=key, Body=data, ContentType=suffix_map[file_path.suffix])
            log_success(f'Files uploaded successfully.')
        except ClientError as e:
            terminate(f'Unable to upload files: {e}.', ErrCode.EXCEPTION)