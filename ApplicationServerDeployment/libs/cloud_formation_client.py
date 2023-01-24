# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from time import sleep

from libs.utils import *


class CloudFormationClient:
    """
    Provides Cloud Formation client with methods necessary to deploy/delete stack.

    Attributes
    ----------
        _client: botocore.client.CloudFormation
            Client to AWS Cloud Formation.

    """
    SSA_STACK = 'SidewalkSampleApplicationStack'

    def __init__(self, session: boto3.Session):
        self._client = session.client(service_name='cloudformation')

    # -------
    # Deploy
    # -------
    def create_stack(self, template: str, sid_dest: str, dest_exists: bool):
        """
        Creates SidewalkSampleApplicationStack.

        :param template:        Cloud formation template.
        :param sid_dest:        Sidewalk destination to be used.
        :param dest_exists:     If True, Sidewalk destination will be created as a part of the stack.
                                If False, it is assumed that destination already exists.
        """
        sidewalk_stack_name = 'SidewalkSampleApplicationStack'
        log_info(f'Creating {sidewalk_stack_name} from cloud formation template...')
        try:
            stack_name = sidewalk_stack_name
            response = self._client.create_stack(
                StackName=stack_name,
                TemplateBody=template,
                Parameters=[
                    {
                        'ParameterKey': 'SidewalkDestinationName',
                        'ParameterValue': sid_dest
                    },
                    {
                        'ParameterKey': 'SidewalkDestinationAlreadyExists',
                        'ParameterValue': "true" if dest_exists else "false"
                    },
                    {
                        'ParameterKey': 'DeployGrafana',
                        'ParameterValue': "false"
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'SidewalkSampleApplication'
                    },
                ],
                TimeoutInMinutes=10,
                OnFailure='DELETE'
            )
            stack_status = ''
            stack_events = []
            in_progress = True
            while in_progress:
                response = self._client.describe_stacks(StackName=stack_name)
                stack_status = response['Stacks'][0]['StackStatus']
                status_end = stack_status.split('_')[-1]
                if status_end in ['COMPLETE', 'FAILED']:
                    in_progress = False
                response = self._client.describe_stack_events(StackName=stack_name)
                stack_events_idx = len(stack_events)
                stack_events = list(reversed(response['StackEvents']))
                for event in stack_events[stack_events_idx:]:
                    timestamp = str(event.get('Timestamp')).split('.')[0].split('+')[0]
                    logical_id = event.get('LogicalResourceId', None)
                    status = event.get('ResourceStatus', None)
                    log_progress(f'[{timestamp}] \t{status}: {logical_id}')
                if in_progress:
                    sleep(1)
            if stack_status == 'CREATE_COMPLETE':
                log_success(f'{sidewalk_stack_name} created successfully.')
            else:
                terminate(
                    f'{sidewalk_stack_name} creation failed. Status found: {stack_status}, status expected: CREATE_COMPLETE',
                    ErrCode.EXCEPTION
                )
        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                log_success(f'{sidewalk_stack_name} already exists, skipping.')
            else:
                terminate(f'{sidewalk_stack_name} creation failed: {e}.', ErrCode.EXCEPTION)

    def update_stack(self, deploy_grafana: bool):
        """
        Updates existing stack by adding/removing Grafana related resources.

        :param deploy_grafana:      If True, Grafana related resources are included in the template.
        """
        if deploy_grafana:
            log_info(f'Updating {self.SSA_STACK} stack with Grafana-related resources...')
        else:
            log_info(f'Removing Grafana-related resources from {self.SSA_STACK} stack...')
        try:
            response = self._client.update_stack(
                StackName=self.SSA_STACK,
                UsePreviousTemplate=True,
                Parameters=[
                    {
                        'ParameterKey': 'SidewalkDestinationAlreadyExists',
                        'ParameterValue': "true"
                    },
                    {
                        'ParameterKey': 'DeployGrafana',
                        'ParameterValue': "true" if deploy_grafana else "false"
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'SidewalkSampleApplication'
                    },
                ],
                DisableRollback=False
            )
            stack_status = ''
            stack_events = []
            in_progress = True
            while in_progress:
                response = self._client.describe_stacks(StackName=self.SSA_STACK)
                stack_status = response['Stacks'][0]['StackStatus']
                status_end = stack_status.split('_')[-1]
                if status_end in ['COMPLETE', 'FAILED']:
                    in_progress = False
                response = self._client.describe_stack_events(StackName=self.SSA_STACK)
                stack_events_idx = len(stack_events)
                stack_events = list(reversed(response['StackEvents']))
                for event in stack_events[stack_events_idx:]:
                    timestamp = str(event.get('Timestamp')).split('.')[0].split('+')[0]
                    logical_id = event.get('LogicalResourceId', None)
                    status = event.get('ResourceStatus', None)
                    log_progress(f'[{timestamp}] \t{status}: {logical_id}')
                if in_progress:
                    sleep(1)
            if stack_status == 'UPDATE_COMPLETE':
                log_success(f'{self.SSA_STACK} updated successfully.')
            else:
                terminate(
                    f'{self.SSA_STACK} update failed. Status found: {stack_status}, status expected: CREATE_COMPLETE',
                    ErrCode.EXCEPTION
                )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError' and 'No updates' in e.response['Error']['Message']:
                if deploy_grafana:
                    log_success(f'Grafana resources already exist in {self.SSA_STACK} stack, skipping.')
                else:
                    log_success(f'Grafana resources are not part of {self.SSA_STACK} stack, skipping.')
            elif e.response['Error']['Code'] == 'ValidationError' and 'does not exist' in e.response['Error']['Message']:
                log_success(f'{self.SSA_STACK} stack does not exist, skipping.')
            else:
                terminate(f'{self.SSA_STACK} update failed: {e}.', ErrCode.EXCEPTION)

    def get_output_var(self, key: str) -> str:
        """
        Gets stack output variable value.

        :param key:     Output variable key.
        :returns:       Value associated with the given key. Returns 'None' if variable not found.
        """
        try:
            log_info(f'Getting {key} value from the {self.SSA_STACK} stack Outputs...')
            value = ''
            response = self._client.describe_stacks(StackName=self.SSA_STACK)
            outputs = response['Stacks'][0]['Outputs']
            for output in outputs:
                if output['OutputKey'] == key:
                    value = output['OutputValue']
                    break
            if value:
                log_success(f'Value read successfully.')
                return value
            else:
                raise KeyError(f'Key {key} not found in Outputs.')
        except (IndexError, KeyError, ClientError) as e:
            return None

    # -------
    # Delete
    # -------
    def delete_stack(self):
        """
        Deletes SidewalkSampleApplicationStack.
        """
        log_info(f'Deleting {self.SSA_STACK} from cloud formation template...')
        try:
            # check if the stack exists
            response = self._client.describe_stacks(StackName=self.SSA_STACK)
            stack_status = response['Stacks'][0]['StackStatus']
            # get stack_id so describe_stacks & describe_stack_events doesn't fail after deletion
            stack_id = response['Stacks'][0]['StackId']
            # delete stack
            stack_status, failures = self._delete_stack(stack_id)
            if stack_status == 'DELETE_COMPLETE':
                log_success(f'{self.SSA_STACK} deleted successfully.')
            elif 'SidewalkDestination' in failures and self.SSA_STACK in failures and len(failures) == 2:
                # if only destination removal failed, retry to delete stack, while retaining SidewalkDestination
                failures.remove(self.SSA_STACK)
                log_warn('Cannot delete destination because at least 1 device with destination exists. '
                         'Retrying to remove the stack, while keeping the SidewalkDestination...')
                stack_status, _ = self._delete_stack(stack_id, failures)
                if stack_status == 'DELETE_COMPLETE':
                    log_success(f'{self.SSA_STACK} deleted successfully. SidewalkDestination left untouched.')
                else:
                    terminate(
                        f'{self.SSA_STACK} deletion failed. Status found: {stack_status}, status expected: DELETE_COMPLETE',
                        ErrCode.EXCEPTION
                    )
            else:
                terminate(
                    f'{self.SSA_STACK} deletion failed. Status found: {stack_status}, status expected: DELETE_COMPLETE',
                    ErrCode.EXCEPTION
                )
        except ClientError as e:
            # will hit this if the initial describe_stacks fails with sidewalk_stack_name
            if e.response['Error']['Code'] == 'ValidationError':
                log_success(f'{self.SSA_STACK} doesn\'t exist, skipping.')
            else:
                terminate(f'{self.SSA_STACK} deletion failed: {e}.', ErrCode.EXCEPTION)

    def _delete_stack(self, stack_id: str, retain_resources: list = None) -> (str, list):
        """Removes CloudFormation stack with option to retain resources.

        :param stack_id:            The name or the unique stack ID that's associated with the stack.
        :param retain_resources:    Tuple of logical IDs of the resources you want to retain.
                                    Applies for stack in the DELETE_FAILED state.
        :returns:                   (stack deletion status, [logical IDs of resources, which removal failed])
        """
        start_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        stack_status = ''
        stack_events = []
        failures = []
        in_progress = True
        if retain_resources:
            self._client.delete_stack(StackName=stack_id, RetainResources=retain_resources)
        else:
            self._client.delete_stack(StackName=stack_id)
        while in_progress:
            response = self._client.describe_stacks(StackName=stack_id)
            stack_status = response['Stacks'][0]['StackStatus']
            status_end = stack_status.split('_')[-1]
            if status_end in ['COMPLETE', 'FAILED']:
                in_progress = False
            response = self._client.describe_stack_events(StackName=stack_id)
            stack_events_idx = len(stack_events)
            stack_events = list(reversed(response['StackEvents']))
            for event in stack_events[stack_events_idx:]:
                timestamp = str(event.get('Timestamp')).split('.')[0].split('+')[0]
                # skip events from before deletion
                if timestamp < start_timestamp: continue
                logical_id = event.get('LogicalResourceId', None)
                status = event.get('ResourceStatus', None)
                log_progress(f'[{timestamp}] \t{status}: {logical_id}')
                if status == 'DELETE_FAILED':
                    failures.append(logical_id)
            if in_progress: sleep(1)
        return stack_status, failures
