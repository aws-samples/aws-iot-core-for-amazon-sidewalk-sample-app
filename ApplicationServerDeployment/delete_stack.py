# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deletes SidewalkSampleApplication stack.
It deletes also Grafana-related resources (if exist).
"""

import boto3

from constants.GrafanaConstants import DESTINATION_ROLE as GRAFANA_DESTINATION_ROLE
from constants.SampleApplicationConstants import *
from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.s3_client import S3Client
from libs.utils import *
from libs.iot_wireless_client import IoTWirelessClient


SSA_STACK = 'SidewalkSampleApplicationStack'


# -----------------
# Read config file
# -----------------
config = Config()


# --------------------
# Ask user to proceed
# --------------------
log_info('Arguments to be used during the SidewalkSampleApplication deletion:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_info(f'\tREGION: {config.region_name}')
if config.interactive_mode:
    log_warn('This is a destructive action and can not be undone!')
    confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
cf_client = CloudFormationClient(session)
s3_client = S3Client(session)
wireless_client = IoTWirelessClient(session)

# --------------------------------------
# Delete bucket contents
# --------------------------------------
bucket = cf_client.get_output_var(SSA_STACK, "SidewalkWebAppBucketName")
if bucket:
    s3_client.delete_bucket_content(bucket)

ota_bucket = cf_client.get_output_var(SSA_STACK, "SidewalkOTASourceBucketName")
if ota_bucket:
    s3_client.delete_bucket_content(ota_bucket)

if CFN_BUCKET_NAME:
    s3_client.delete_bucket_content(CFN_BUCKET_NAME)
    s3_client.delete_bucket(CFN_BUCKET_NAME)

# --------------------------------------
# Delete CloudFormation stack
# --------------------------------------
cf_client.delete_stack(stack_name=STACK_NAME)
config.set_web_app_url(None)


# -------------------------
# Print success message
# -------------------------
log_success('---------------------------------------------------------------')
log_success('The SidewalkSampleApplication has been deleted.')
log_success('---------------------------------------------------------------')


# --------------------------------------------------------------------------------
# Check if destination still exists.
# If True, try to reassign to it an existing destination role from another stack,
# so that destination keeps permissions to publish to the sidewalk/app_data topic
# --------------------------------------------------------------------------------
wireless_client.reassign_role_to_destination(
    dest_name=config.sid_dest_name,
    role_name=GRAFANA_DESTINATION_ROLE
)
