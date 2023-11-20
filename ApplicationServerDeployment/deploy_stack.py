# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deploys SidewalkSampleApplication stack.
"""
from time import sleep

import boto3
import webbrowser

from botocore.exceptions import ClientError

from constants.SampleApplicationConstants import *
from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.s3_client import S3Client
from libs.utils import *
from libs.iot_wireless_client import IoTWirelessClient
from libs.lambda_client import LambdaClient

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
if config.interactive_mode:
    log_info(f'Proceed with stack creation?')
    confirm()

# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# Sidewalk is only enabled in the us-east-1 region
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
cf_client = CloudFormationClient(session)
s3_client = S3Client(session)
wireless_client = IoTWirelessClient(session)
lambda_client = LambdaClient(session)
api_gateway_client = session.client(service_name='apigateway')

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
s3_cfn_bucket_name = 'sidewalk-sample-app-stack'
s3_cfn_template_key = 'SidewalkSampleApplicationStack.yaml'
stack_path = Path(__file__).parent.joinpath('template', 'SidewalkSampleApplicationStack.yaml')
s3_client.upload_template_to_s3(stack_path, s3_cfn_bucket_name, s3_cfn_template_key)
stack = read_file(stack_path)
templateUrl = 'https://' + s3_cfn_bucket_name + '.s3.amazonaws.com/' + s3_cfn_template_key
# --------------------------------------
# Trigger CloudFormation stack creation
# --------------------------------------
cf_client.create_stack(
    templateUrl=templateUrl,
    stack_name=STACK_NAME,
    sid_dest=config.sid_dest_name,
    dest_exists=sid_dest_already_exists,
    tag=TAG
)

# ------------------------
# Clear auth api-gw cache
# ------------------------
api_gateway_id = cf_client.get_output_var(STACK_NAME, 'SidewalkApiId')
api_gateway_client.flush_stage_authorizers_cache(restApiId=api_gateway_id, stageName="dev")

# ------------------------------------------------------------------------
# Update given Sidewalk destination (only if destination already existed)
# ------------------------------------------------------------------------
if sid_dest_already_exists:
    wireless_client.update_existing_destination(
        dest_name=config.sid_dest_name,
        role_name=DESTINATION_ROLE,
        interactive_mode=config.interactive_mode
    )

# --------------------
# Update lambdas code
# --------------------
parent = Path(__file__).parent
lambdas = ['SidewalkUplinkLambda', 'SidewalkDownlinkLambda', 'SidewalkDbHandlerLambda']
dirs = ['uplink', 'downlink', 'db_handler']
common_dirs = ['codec', 'database', 'utils']
lambda_client.upload_lambda_files(parent, lambdas, dirs, common_dirs)
auth_lambdas = ['SidewalkUserAuthenticatorLambda', 'SidewalkTokenAuthenticatorLambda', 'SidewalkTokenGeneratorLambda']
auth_dirs = ['authUser', 'authApiGw', 'authRequestSigner']
auth_library_dirs = ['authLibs']
lambda_client.upload_lambda_files(parent, auth_lambdas, auth_dirs, auth_library_dirs)
ota_lambdas = ['SidewalkOTAStartTransferLambda', 'SidewalkOTACancelTransferLambda', 'SidewalkOTAGetS3FilesLambda', 'SidewalkOTAUploadFileLambda', 'SidewalkOTADbHandlerLambda']
ota_dirs = ['ota', 'ota', 'ota', 'ota', 'db_handler']
ota_lib_dirs = ['utils', 'database', 'utils', 'utils','database']
lambda_client.upload_lambda_files(parent, ota_lambdas, ota_dirs, ota_lib_dirs)
auth_string = config.get_username_and_password_as_base64()
env_variables = {"CREDENTIALS": auth_string}
lambda_client.update_lambda_env_variables(auth_lambdas, env_variables)

# ---------------------------
# Upload WebApp assets to S3
# ---------------------------
bucket_name = cf_client.get_output_var(STACK_NAME, 'SidewalkWebAppBucketName')
s3_client.put_files(bucket_name, Path(__file__).parent.joinpath('gui', 'build'))

# --------------------------------
# Print Sensor Monitoring App URL
# --------------------------------
web_app_url = cf_client.get_output_var(STACK_NAME, 'CloudFrontDistribution')
config.set_web_app_url(web_app_url)
webbrowser.open(f'https://{web_app_url}')

log_success('---------------------------------------------------------------')
log_success('Opening Sensor Monitoring App on the following link:')
log_success(f'https://{web_app_url}')
log_success(f'This URL has been saved to config.yaml Outputs.WEB_APP_URL')
log_success('---------------------------------------------------------------')
