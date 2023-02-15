# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deletes SidewalkGrafana stack.
"""

import boto3

from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.grafana_client import GrafanaClient
from libs.identity_store_client import IdentityStoreClient
from libs.utils import *
from libs.wireless_client import WirelessClient


# -----------------
# Read config file
# -----------------
config = Config()


# --------------------
# Ask user to proceed
# --------------------
log_info('Arguments to be used during the SidewalkGrafana deletion:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_info(f'\tREGION: {config.region_name}')
log_warn('This is a destructive action and can not be undone!')
confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
cf_client = CloudFormationClient(session)
grafana_client = GrafanaClient(session)
idstore_client = IdentityStoreClient(session, config.identity_store_id)
wireless_client = WirelessClient(session)

# --------------------------------------
# Delete CloudFormation stack
# --------------------------------------
cf_client.delete_stack(name=cf_client.GRAFANA_STACK)


# --------------------------------------------------------------------------------
# Check if destination still exists.
# If True, try to reassign to it an existing destination role from another stack,
# so that destination keeps permissions to publish to the sidewalk/app_data topic
# --------------------------------------------------------------------------------
wireless_client.reassign_role_to_destination(dest_name=config.sid_dest_name)


# ----------------------------------------
# Delete Amazon Managed Grafana workspace
# ----------------------------------------
grafana_client.delete_workspace()
config.set_workspace_url(None)


# ---------------------------------
# Delete IAM Identity Center group
# ---------------------------------
if config.identity_store_id:
    idstore_client.delete_group()
else:
    log_warn(f'IDENTITY_STORE_ID not given. If IAM Identity Center group/users were created, they will not be removed.')


# -------------------------
# Print success message
# -------------------------
log_success('---------------------------------------------------------------')
log_success('The SidewalkGrafana has been deleted.')
log_success('---------------------------------------------------------------')


# ----------------------------------------------
# Optionally: delete users given in config file
# ----------------------------------------------
if config.identity_store_id and config.identity_center_users:
    log_info('Do you want to delete following IAM Identity Center users?')
    for idx, user in enumerate(config.identity_center_users):
        log_info(f'\t{idx + 1}. {user.username}')
    confirm()
    for user in config.identity_center_users:
        idstore_client.delete_user(user)
