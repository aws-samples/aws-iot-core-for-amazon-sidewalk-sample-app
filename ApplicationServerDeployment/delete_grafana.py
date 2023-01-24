# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script deletes Grafana-related resources only.
"""

import boto3

from libs.cloud_formation_client import CloudFormationClient
from libs.config import Config
from libs.grafana_client import GrafanaClient
from libs.identity_store_client import IdentityStoreClient
from libs.utils import *


# -----------------
# Read config file
# -----------------
config = Config()


# --------------------
# Ask user to proceed
# --------------------
log_info('Arguments to be used during the Grafana-related resources deletion:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_warn('This is a destructive action and can not be undone!')
confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile)
cf_client = CloudFormationClient(session)
grafana_client = GrafanaClient(session)
idstore_client = IdentityStoreClient(session, config.identity_store_id)


# ------------------------------------------------------------------
# Update CloudFormation stack by removing Grafana-related resources
# ------------------------------------------------------------------
cf_client.update_stack(deploy_grafana=False)


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
log_success('Grafana related resources has been deleted.')
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
