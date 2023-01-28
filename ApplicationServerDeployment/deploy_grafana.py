# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script extends SidewalkSampleApplication stack by creating data sources for Grafana.
It also creates Grafana workspace and configures dashboard.

IMPORTANT!
You need to deploy SidewalkSampleApplication stack first.
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
log_info('Arguments to be used during the SidewalkSampleApplication deployment:')
log_info(f'\tCONFIG_PROFILE: {config.aws_profile}')
log_info(f'\tREGION: {config.region_name}')
msg = f"{config.identity_store_id}" if config.identity_store_id else "<empty> - no users will be created"
log_info(f'\tIDENTITY_STORE_ID: {msg}')
if config.identity_store_id and config.identity_center_users:
    log_info(f'\tIDENTITY_CENTER_USERS: ')
    for idx, user in enumerate(config.identity_center_users):
        log_info(
            f'\t\t{idx + 1}.'
            f'{user.username}'
            f', {user.firstname}'
            f', {user.lastname}')
elif config.identity_store_id:
    log_info(f'\tIDENTITY_CENTER_USERS: no valid entries found; no users will be created')
else:
    pass
log_info(f'Proceed with stack creation?')
confirm()


# -------------------------------------------------------------
# Create boto3 session using given profile and service clients
# -------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
cf_client = CloudFormationClient(session)
grafana_client = GrafanaClient(session)
idstore_client = IdentityStoreClient(session, config.identity_store_id)


# ------------------------------------
# Trigger CloudFormation stack update
# ------------------------------------
cf_client.update_stack(deploy_grafana=True)


# ------------------------------------------------------
# Create and configure Amazon Managed Grafana workspace
# ------------------------------------------------------

# Create workspace
workspace_id, workspace_url = grafana_client.create_workspace()

# Store workspace url in config.json
config.set_workspace_url(workspace_url)

# Create workspace API key
workspace_api_key = grafana_client.create_workspace_api_key(workspace_id)

# Add timestream datasource
grafana_client.init_http_client(workspace_url, workspace_api_key)
datasource_uid = grafana_client.ws_add_datasource()

# Create dashboard from template
dashboard_id = grafana_client.ws_create_dashboard(
    template=Path(__file__).parent.joinpath('template', 'SidewalkSampleApplicationDashboard.json'),
    datasource_uid=datasource_uid
)

# Set the home dashboard
grafana_client.ws_set_home_dashboard(dashboard_id)

# Remove workspace API key
grafana_client.delete_workspace_api_key(workspace_id)


# -------------------------
# Print login info
# -------------------------
log_success('---------------------------------------------------------------')
log_success('Your Grafana workspace is ready. Log in using the link below:')
log_success(f'https://{workspace_url}')
log_success('---------------------------------------------------------------')


# -----------------------------------------------------
# Configure users with access to the Grafana workspace
# -----------------------------------------------------
if not (config.identity_store_id and config.identity_center_users):
    log_warn("IDENTITY_STORE_ID or IDENTITY_CENTER_USERS not given. Users will not be created.")
else:
    log_info(f'Creating users for the Grafana workspace...')
    confirm()

    # Create group in IAM Identity Center
    group_id = idstore_client.create_group()

    # Create user in IAM Identity Center
    for idx, user in enumerate(config.identity_center_users):
        user.id = idstore_client.create_user(user)

    # Add users to the group
    for idx, user in enumerate(config.identity_center_users):
        idstore_client.add_user_to_group(user, group_id)
