# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deploys SidewalkSampleApplication stack.
"""

import boto3
import webbrowser

from botocore.exceptions import ClientError
from io import BytesIO

from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.s3_client import S3Client
from libs.utils import *
from libs.wireless_client import WirelessClient


# -----------------
# Read config file
# -----------------
config = Config()


# --------------------
# Ask user to proceed
# --------------------
log_info('Arguments to be used during the SidewalkSampleApplication deployment:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_info(f'\tREGION: {config.region_name}')
log_info(f'\tSIDEWALK_DESTINATION: {config.sid_dest_name}')
log_info(f'This can take several minutes to complete.')
log_info(f'Proceed with stack creation?')
confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# Sidewalk is only enabled in the us-east-1 region
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
cf_client = CloudFormationClient(session)
lambda_client = session.client(service_name='lambda')
s3_client = S3Client(session)
wireless_client = WirelessClient(session)


# ------------------------------------
# Enable Sidewalk event notifications
# ------------------------------------
wireless_client.enable_notifications()

# ---------------------------------------------------
# Check if given Sidewalk destination already exists
# ---------------------------------------------------
sid_dest_already_exists = wireless_client.check_if_destination_exists(name=config.sid_dest_name)


# -----------------------------
# Read CloudFormation template
# -----------------------------
stack_path = Path(__file__).parent.joinpath('template', 'SidewalkSampleApplicationStack.yaml')
stack = read_file(stack_path)


# --------------------------------------
# Trigger CloudFormation stack creation
# --------------------------------------
cf_client.create_stack(
    template=stack,
    name=cf_client.SSA_STACK,
    sid_dest=config.sid_dest_name,
    dest_exists=sid_dest_already_exists,
    tag='SidewalkSampleApplication'
)


# ------------------------------------------------------------------------
# Update given Sidewalk destination (only if destination already existed)
# ------------------------------------------------------------------------
if sid_dest_already_exists:
    wireless_client.update_existing_destination(
        dest_name=config.sid_dest_name,
        role_name=wireless_client.SSA_DESTINATION_ROLE
    )


# --------------------
# Update lambdas code
# --------------------
lambdas = ['SidewalkUplinkLambda', 'SidewalkDownlinkLambda', 'SidewalkDbHandlerLambda']
dirs = ['uplink', 'downlink', 'db_handler']
parent = Path(__file__).parent

for idx, (lam, dir) in enumerate(zip(lambdas, dirs)):
    buffer = BytesIO()
    log_info(f'Uploading {lam} files...')
    zip_top_level_files(parent.joinpath('lambda', 'codec'), buffer)
    zip_top_level_files(parent.joinpath('lambda', 'database'), buffer)
    zip_top_level_files(parent.joinpath('lambda', 'utils'), buffer)
    zip_top_level_files(parent.joinpath('lambda', dir), buffer)
    try:
        response = lambda_client.update_function_code(FunctionName=lam, ZipFile=buffer.getvalue())
        eval_client_response(response, f'{lam} function updated.')
    except ClientError as e:
        terminate(f'Unable to update lambda: {e}.', ErrCode.EXCEPTION)


# ---------------------------
# Upload WebApp assets to S3
# ---------------------------
bucket_name = cf_client.get_output_var('SidewalkWebAppBucketName')
s3_client.put_files(bucket_name, Path(__file__).parent.joinpath('gui', 'build'))

# --------------------------------
# Print Sensor Monitoring App URL
# --------------------------------
web_app_url = cf_client.get_output_var('CloudFrontDistribution')
config.set_web_app_url(web_app_url)
webbrowser.open(f'https://{web_app_url}')

log_success('---------------------------------------------------------------')
log_success('Opening Sensor Monitoring App on the following link:')
log_success(f'https://{web_app_url}')
log_success(f'This URL has been saved to config.yaml Outputs.WEB_APP_URL')
log_success('---------------------------------------------------------------')
