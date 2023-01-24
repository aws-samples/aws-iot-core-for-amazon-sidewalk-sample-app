# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from time import sleep

from libs.grafana import Grafana
from libs.utils import *


class GrafanaClient:
    """
    Provides Grafana client with methods necessary to deploy/delete stack.

    Attributes
    ----------
        _grafana_client: botocore.client.ManagedGrafana
            Client to AWS Managed Grafana.
        _iam_client: botocore.client.IAM
            Client to AWS IAM.
        _grafana_http_client: libs.grafana.Grafana
            Client for Grafana http api calls
        _region: str
            AWS region for a current session.

    """
    WORKSPACE = 'SidewalkSampleApplicationGrafanaWorkspace'
    WORKSPACE_API_KEY = f'{WORKSPACE}ApiKey'
    DATASOURCE = 'SidewalkTimestream'
    DASHBOARD = 'SidewalkSampleApplication'

    def __init__(self, session: boto3.Session):
        self._grafana_client = session.client(service_name='grafana')
        self._iam_client = session.client(service_name='iam')
        self._grafana_http_client = None
        self._region = session.region_name

    # -------
    # Deploy
    # -------
    def create_workspace(self) -> (str, str):
        """
        Creates Grafana workspace.

        :return:    (workspace_id, workspace_url) Tuple with metadata of created workspace.
        """
        workspace_id = ''
        workspace_url = ''
        log_info(f'Creating {self.WORKSPACE} in Amazon Grafana...')
        confirm()

        try:
            for ws in self._grafana_client.list_workspaces()['workspaces']:
                if self.WORKSPACE == ws['name']:
                    workspace_id = ws['id']
                    workspace_url = f'{workspace_id}.grafana-workspace.{self._region}.amazonaws.com'
                    raise FileExistsError
            response = self._iam_client.get_role(RoleName=f'{self.WORKSPACE}Role')
            workspace_role_arn = response['Role']['Arn']
            response = self._grafana_client.create_workspace(
                accountAccessType='CURRENT_ACCOUNT',
                authenticationProviders=['AWS_SSO'],
                permissionType='CUSTOMER_MANAGED',
                tags={'Application': 'SidewalkSampleApplication'},
                workspaceDataSources=['TIMESTREAM'],
                workspaceDescription='Workspace for SidewalkSampleApplication',
                workspaceName=self.WORKSPACE,
                workspaceRoleArn=workspace_role_arn
            )
            in_progress = True
            workspace_id = response['workspace']['id']
            workspace_status = ''
            while in_progress:
                response = self._grafana_client.describe_workspace(workspaceId=workspace_id)
                if workspace_status != response['workspace']['status']:
                    workspace_status = response['workspace']['status']
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    log_progress(f"[{timestamp}] \t{workspace_status}: {self.WORKSPACE}")
                if workspace_status in ['ACTIVE', 'FAILED', 'CREATION_FAILED']:
                    in_progress = False
                sleep(1)

            if workspace_status == 'ACTIVE':
                workspace_url = f'{workspace_id}.grafana-workspace.{self._region}.amazonaws.com'
                log_success(f'{self.WORKSPACE} created successfully. Workspace url: {workspace_url}')
            else:
                terminate(
                    f'{self.WORKSPACE} creation failed. Status found: {workspace_status}, status expected: ACTIVE',
                    ErrCode.EXCEPTION
                )
        except FileExistsError:
            log_success(
                f'{self.WORKSPACE} already exists: {workspace_id}.grafana-workspace.{self._region}.amazonaws.com, skipping.')
        except ClientError as e:
            terminate(f'{self.WORKSPACE} creation failed: {e}.', ErrCode.EXCEPTION)
        return workspace_id, workspace_url

    def create_workspace_api_key(self, workspace_id: str) -> str:
        """
        Creates workspace api key.

        :param:     Workspace id.
        :return:    Workspace api key.
        """
        workspace_api_key = ''
        try:
            log_info("Creating workspace API key...")
            response = self._grafana_client.create_workspace_api_key(
                keyName=self.WORKSPACE_API_KEY, keyRole='ADMIN', secondsToLive=900, workspaceId=workspace_id
            )
            workspace_api_key = response['key']
        except ClientError:
            # Try to delete and recreate API key
            try:
                self._grafana_client.delete_workspace_api_key(
                    keyName=self.WORKSPACE_API_KEY, workspaceId=workspace_id
                )
                response = self._grafana_client.create_workspace_api_key(
                    keyName=self.WORKSPACE_API_KEY, keyRole='ADMIN', secondsToLive=900, workspaceId=workspace_id
                )
                workspace_api_key = response['key']
            except (ClientError, KeyError) as e:
                terminate(f'Unable to create {self.WORKSPACE_API_KEY}: {e}.', ErrCode.EXCEPTION)
        log_success('API key created.')
        return workspace_api_key

    def init_http_client(self, workspace_url: str, workspace_api_key: str):
        """
        Initializes client for Grafana http api calls

        :param workspace_url:       Workspace url.
        :param workspace_api_key:   Workspace api key to be used to authorize calls.
        """
        self._grafana_http_client = Grafana(workspace_url, workspace_api_key)

    def ws_add_datasource(self) -> str:
        """
        Adds datasource to the Grafana workspace.

        :return:    Datasource uid.
        """
        self._check_http_client()
        datasource_uid = ''
        try:
            payload = {
                "name": self.DATASOURCE,
                "type": "grafana-timestream-datasource",
                "typeName": "Amazon Timestream",
                "access": "proxy",
                "basicAuth": False,
                "isDefault": True,
                "jsonData": {
                    "authType": "ec2_iam_role",
                    "defaultDatabase": "\"SidewalkTimestream\"",
                    "defaultMeasure": "",
                    "defaultRegion": "us-east-1"
                },
                "readOnly": False
            }
            log_info('Adding timestream database as a Grafana datasource...')
            status, response, datasource_uid = self._grafana_http_client.create_data_source(payload)
            if status:
                log_success(f'{self.DATASOURCE} datasource added.')
            elif response.status_code == 409:
                log_info(f'{self.DATASOURCE} datasource already exists, getting its uid...')
                status, response, datasource_uid = self._grafana_http_client.get_data_source(self.DATASOURCE)
                if status:
                    log_success(f'{self.DATASOURCE} datasource in place.')
                else:
                    terminate(f'Unexpected status code: {response.status_code}. Message: {response.content}',
                              ErrCode.EXCEPTION)
            else:
                terminate(f'Unexpected status code: {response.status_code}. Message: {response.content}',
                          ErrCode.EXCEPTION)
        except Exception as e:
            terminate(f'Exception was thrown: {e}.', ErrCode.EXCEPTION)
        return datasource_uid

    def ws_create_dashboard(self, template: Path, datasource_uid: str) -> str:
        """
        Adds Grafana dashboard to the workspace using given template file.

        :param template:        Path to the template
        :param datasource_uid   Datasource uid
        :return:                Dashboard id.
        """
        self._check_http_client()
        dashboard_id = ''
        try:
            template = read_file(template)
            log_info("Adding SidewalkTestApplication dashboard to Grafana...")
            template = template.replace("<datasource_uid>", datasource_uid)
            dashboard_template = json.loads(template)
            payload = {
                "dashboard": dashboard_template,
                "message": "Creating SidewalkSampleApplication dashboard",
                "overwrite": True
            }
            status, response, dashboard_id = self._grafana_http_client.create_dashboard(payload)
            if status:
                log_success(f'{self.DASHBOARD} dashboard added.')
            else:
                terminate(f'Unexpected status code: {response.status_code}. Message: {response.content}',
                          ErrCode.EXCEPTION)
        except Exception as e:
            terminate(f'Exception was thrown: {e}.', ErrCode.EXCEPTION)
        return dashboard_id

    def ws_set_home_dashboard(self, dashboard_id: str):
        """
        Sets home dashboard of the workspace.

        :param dashboard_id:    Dashboard id.
        """
        self._check_http_client()
        try:
            log_info("Setting the dashboard as a home dashboard...")
            payload = {"homeDashboardId": dashboard_id}
            status, response = self._grafana_http_client.update_org_preferences(payload)
            if status:
                log_success(f'{self.DASHBOARD} dashboard added.')
            else:
                terminate(f'Unexpected status code: {response.status_code}. Message: {response.content}',
                          ErrCode.EXCEPTION)
        except Exception as e:
            terminate(f'Exception was thrown: {e}.', ErrCode.EXCEPTION)

    # -------
    # Delete
    # -------
    def delete_workspace(self):
        """
        Deletes Grafana workspace.
        """
        log_info(f'Deleting {self.WORKSPACE} from Amazon Grafana...')
        workspace_id = ''
        try:
            for ws in self._grafana_client.list_workspaces()['workspaces']:
                if self.WORKSPACE == ws['name']:
                    workspace_id = ws['id']
            if not workspace_id:
                raise FileNotFoundError
            self._grafana_client.delete_workspace(workspaceId=workspace_id)
            workspace_status = ''
            # loop ends when deletion completes and grafana_client.describe_workspace throws ResourceNotFoundException
            while True:
                response = self._grafana_client.describe_workspace(workspaceId=workspace_id)
                if workspace_status != response['workspace']['status']:
                    workspace_status = response['workspace']['status']
                    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    log_progress(f"[{timestamp}] \t{workspace_status}: {self.WORKSPACE}")
                if workspace_status != 'DELETING':
                    terminate(
                        f'{self.WORKSPACE} deletion failed. Status found: {workspace_status}', ErrCode.EXCEPTION
                    )
                sleep(1)
        except FileNotFoundError:
            log_success(f'{self.WORKSPACE} doesn\'t exist, skipping.')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                log_progress(f"[{timestamp}] \tDELETE_COMPLETE: {self.WORKSPACE}")
                log_success(f'{self.WORKSPACE} successfully deleted')
            elif e.response['Error']['Code'] == 'ConflictException':
                msg = e.response['Error']['Message']
                terminate(f'{msg}.', ErrCode.EXCEPTION)
            else:
                terminate(f'{self.WORKSPACE} deletion failed: {e}.', ErrCode.EXCEPTION)

    def delete_workspace_api_key(self, workspace_id: str):
        """
        Deletes workspace api key.

        :param:     Workspace id.
        """
        try:
            log_info("Removing workspace API key...")
            response = self._grafana_client.delete_workspace_api_key(
                workspaceId=workspace_id, keyName=self.WORKSPACE_API_KEY
            )
            eval_client_response(response, 'API key deleted.')
        except ClientError as e:
            terminate(f'Unable to delete {self.WORKSPACE_API_KEY}: {e}.', ErrCode.EXCEPTION)

    # ------
    # Utils
    # ------
    def _check_http_client(self):
        """
        Checks if http client has been initialized.
        In case of False, terminates program.
        """
        if self._grafana_http_client is None:
            terminate(
                'Grafana http client has not been initialized. Please call "init_http_client" method first.',
                ErrCode.EXCEPTION
            )
