# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deploys SidewalkSampleApplication stack.
"""

import boto3
from botocore.exceptions import ClientError
from io import BytesIO

from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.s3_client import S3Client
from libs.utils import *


# -----------------
# Read config file
# -----------------
config = Config()
region_name = "us-east-1"


# --------------------
# Ask user to proceed
# --------------------
log_info('Arguments to be used during the SidewalkSampleApplication deployment:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_info(f'\t\tregion: {region_name} will be used')
log_info(f'\tSIDEWALK_DESTINATION: {config.sid_dest_name}')
log_info(f'This can take several minutes to complete.')
log_info(f'Proceed with stack creation?')
confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# Sidewalk is only enabled in the us-east-1 region
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=region_name)
cf_client = CloudFormationClient(session)
iam_client = session.client(service_name='iam')
lambda_client = session.client(service_name='lambda')
s3_client = S3Client(session)
wireless_client = session.client(service_name='iotwireless')


# ------------------------------------
# Enable Sidewalk event notifications
# ------------------------------------
try:
    log_info('Enabling Sidewalk event notification in iotwireless...')
    response = wireless_client.update_event_configuration_by_resource_types(
        DeviceRegistrationState={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}},
        Proximity={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}},
        MessageDeliveryStatus={'Sidewalk': {'WirelessDeviceEventTopic': 'Enabled'}}
    )
    eval_client_response(response, 'Notifications enabled.')
except ClientError as e:
    terminate(f'Notifications not enabled: {e}.', ErrCode.EXCEPTION)


# ---------------------------------------------------
# Check if given Sidewalk destination already exists
# ---------------------------------------------------
sid_dest_already_exists = False
try:
    log_info(f'Checking if {config.sid_dest_name} destination exists...')
    response = wireless_client.get_destination(Name=config.sid_dest_name)
    eval_client_response(
        response,
        f'{config.sid_dest_name} already exists and will not be included in the SidewalkSampleApplicationStack.'
    )
    sid_dest_already_exists = True
except ClientError as e:
    if e.response['Error']['Code'] == 'ResourceNotFoundException':
        log_success(f'{config.sid_dest_name} does not exist and will be included in the SidewalkSampleApplicationStack.')
    else:
        terminate(f'Unable to get {config.sid_dest_name} destination: {e}.', ErrCode.EXCEPTION)


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
    sid_dest=config.sid_dest_name,
    dest_exists=sid_dest_already_exists
)


# ------------------------------------------------------------------------
# Update given Sidewalk destination (only if destination already existed)
# ------------------------------------------------------------------------
if sid_dest_already_exists:
    log_info(f'{config.sid_dest_name} already exists and will be modified. Proceed?')
    confirm()
    sid_dest_role = 'SidewalkDestinationRole'
    try:
        log_info(f'Getting {sid_dest_role} role ARN...')
        response = iam_client.get_role(RoleName=f'{sid_dest_role}')
        log_success(f'{sid_dest_role} ARN obtained.')
        log_info(f'Updating {config.sid_dest_name} destination...')
        role_arn = response['Role']['Arn']
        response = wireless_client.update_destination(
            Name=config.sid_dest_name,
            ExpressionType='RuleName',
            Expression='SidewalkUplinkRule',
            Description='Destination for uplink messages from Sidewalk devices.',
            RoleArn=role_arn
        )
        eval_client_response(response, f'{config.sid_dest_name} role updated.')
    except ClientError as e:
        terminate(f'Unable to update {config.sid_dest_name} destination: {e}.', ErrCode.EXCEPTION)


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
api_gw_id = cf_client.get_output_var('SidewalkApiGwId')
bucket_name = cf_client.get_output_var('SidewalkWebAppBucketName')
s3_client.put_files(bucket_name, api_gw_id, Path(__file__).parent.joinpath('gui', 'build'))

# --------------------------------
# Print Sensor Monitoring App URL
# --------------------------------
web_app_url = cf_client.get_output_var('CloudFrontDistribution')
config.set_web_app_url(web_app_url)
os.system(f'open https://{web_app_url}')

log_success('---------------------------------------------------------------')
log_success('Opening Sensor Monitoring App on the following link:')
log_success(f'https://{web_app_url}')
log_success(f'This URL has been saved to config.yaml Outputs.WEB_APP_URL')
log_success('---------------------------------------------------------------')