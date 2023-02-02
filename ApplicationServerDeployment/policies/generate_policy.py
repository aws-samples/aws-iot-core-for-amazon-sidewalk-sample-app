# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Script generates personalized version of the policy templates.
All occurrences of <account_ID> are replaced with the actual AWS account ID, based on the AWS_PROFILE specified in config.yaml.

Outputs:
    - DeployStackPolicy.json - policy with permissions needed to run deploy/delete_stack.py and generate_prototype.py
    - DeployGrafanaPolicy.json - policy with permissions needed to run deploy/delete_grafana.py
"""

import boto3
import os
import sys

from botocore.exceptions import ClientError
from pathlib import Path

# add ApplicationServerDeployment to path
sys.path.append(str(Path(__file__).parents[1].absolute()))
from libs.config import Config
from libs.utils import *

# -----------------
# Read config file
# -----------------
config = Config()

# -----------------------------------------------------------------
# Get AWS account ID based on the profile given in the config file
# -----------------------------------------------------------------
session = boto3.Session(profile_name=config.aws_profile, region_name=config.region_name)
sts_client = session.client(service_name='sts')
try:
    log_info('Fetching AWS account ID based on the caller identity...')
    response = sts_client.get_caller_identity()
    account_id = response["Account"]
    eval_client_response(response, f'Successfully read AWS account ID: {account_id}.')
except ClientError as e:
    terminate(f'Unable to fetch AWS account ID: {e}.', ErrCode.EXCEPTION)

# -----------------------------------
# Generate personalized policy files
# -----------------------------------
policies_path = Path(__file__).parent
templates = [tmpl for tmpl in os.listdir(policies_path) if 'Tmpl' in tmpl]
for tmpl in templates:
    policy = tmpl.replace('Tmpl', '')
    policy_tmpl_content = ''
    log_info(f'Personalizing {tmpl} template using {account_id} AWS account ID...')
    # read template
    with open(policies_path.joinpath(tmpl)) as f:
        policy_tmpl_content = f.read()
    # create policy document
    with open(policies_path.joinpath(policy), 'w') as f:
        f.write(policy_tmpl_content.replace('<account_ID>', account_id))
    log_success(f'{policy} policy created.')
