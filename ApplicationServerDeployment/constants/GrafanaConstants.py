# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

STACK_NAME = 'SidewalkGrafanaStack'
GROUP_NAME = 'SidewalkGrafanaApplicationUsers'
DESTINATION_ROLE = 'GrafanaDestinationRole'
TAG = 'SidewalkGrafana'
WORKSPACE_NAME = 'SidewalkGrafanaWorkspace'
WORKSPACE_ROLE = 'GrafanaWorkspaceRole'
WORKSPACE_API_KEY = f'{WORKSPACE_NAME}ApiKey'
DATASOURCE = 'GrafanaTimestream'
