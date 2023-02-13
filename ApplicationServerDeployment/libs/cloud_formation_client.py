# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
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
    def create_stack(self, template: str, sid_dest: str, dest_exists: bool, tag: str):
        """
        Creates CloudFormation stack.

        :param template:        Cloud formation template.
        :param sid_dest:        Sidewalk destination to be used.
        :param dest_exists:     If True, Sidewalk destination will be created as a part of the stack.
                                If False, it is assumed that destination already exists.
        :param tag:             Tag assigned to created resources; describes application.
        """
        log_info(f'Creating {self.SSA_STACK} from cloud formation template...')
        try:
            response = self._client.create_stack(
                StackName=self.SSA_STACK,
                TemplateBody=template,
                Parameters=[
                    {
                        'ParameterKey': 'SidewalkDestinationName',
                        'ParameterValue': sid_dest
                    },
                    {
                        'ParameterKey': 'SidewalkDestinationAlreadyExists',
                        'ParameterValue': "true" if dest_exists else "false"
                    }
                ],
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': tag
                    },
                ],
                TimeoutInMinutes=10,
                OnFailure='DELETE'
            )
            stack_id = response.get('StackId', self.SSA_STACK)
            stack_status = ''
            event_index = 0
            in_progress = True
            while in_progress:
                response = self._client.describe_stacks(StackName=stack_id)
                stack_status = response['Stacks'][0]['StackStatus']
                status_end = stack_status.split('_')[-1]
                if status_end in ['COMPLETE', 'FAILED']:
                    in_progress = False
                event_index = self._print_stack_events(stack_id=stack_id, pointer=event_index)
                if in_progress: sleep(1)
            if stack_status == 'CREATE_COMPLETE':
                log_success(f'{self.SSA_STACK} created successfully.')
            else:
                terminate(
                    f'{self.SSA_STACK} creation failed. Status found: {stack_status}, status expected: CREATE_COMPLETE',
                    ErrCode.EXCEPTION
                )
        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                log_success(f'{self.SSA_STACK} already exists, skipping.')
            else:
                terminate(f'{self.SSA_STACK} creation failed: {e}.', ErrCode.EXCEPTION)

    def update_stack(self, deploy_grafana: bool):
        """
        Updates existing stack by adding/removing Grafana related resources.

        :param deploy_grafana:      If True, Grafana related resources are included in the template.
        """
        start_timestamp = datetime.now(timezone.utc)
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
            event_index = 0
            in_progress = True
            while in_progress:
                response = self._client.describe_stacks(StackName=self.SSA_STACK)
                stack_status = response['Stacks'][0]['StackStatus']
                status_end = stack_status.split('_')[-1]
                if status_end in ['COMPLETE', 'FAILED']:
                    in_progress = False
                event_index = self._print_stack_events(stack_id=self.SSA_STACK, pointer=event_index, start_date=start_timestamp)
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
            stack_status = self._delete_stack(stack_id)

            if stack_status == 'DELETE_COMPLETE':
                log_success(f'{self.SSA_STACK} deleted successfully.')
                return
            elif stack_status == 'DELETE_FAILED':
                resources = self._client.describe_stack_resources(StackName=stack_id).get('StackResources', [])
                failures = [resource for resource in resources if resource.get('ResourceStatus') == 'DELETE_FAILED']
                # if DELETE_FAILED because of the SidewalkDestination, retry deletion while retaining destination
                if 'SidewalkDestination' in [failure.get('LogicalResourceId') for failure in failures]:
                    log_warn(f'Cannot delete SidewalkDestination. '
                             f'Retrying to remove the stack, while keeping the SidewalkDestination...')
                    stack_status = self._delete_stack(stack_id, ['SidewalkDestination'])
                    if stack_status == 'DELETE_COMPLETE':
                        log_success(f'{self.SSA_STACK} deleted successfully.\n'
                                    f'SidewalkDestination left untouched and can be found under: AWS IoT -> Manage -> LPWAN devices -> Destinations.')
                        return
                # if DELETE_FAILED after retry, print info about resources that failed to be deleted
                if stack_status == 'DELETE_FAILED':
                    resources = self._client.describe_stack_resources(StackName=stack_id).get('StackResources', [])
                    failures = [resource for resource in resources if resource.get('ResourceStatus') == 'DELETE_FAILED']
                    log_error('---------------------------------------------------------------')
                    log_error('Unable to delete following resources:\n')
                    for failure in failures:
                        log_error(f'{failure.get("LogicalResourceId")}'
                                  f'\t{failure.get("ResourceType")}'
                                  f'\n{failure.get("ResourceStatusReason")}\n')
                    log_error('---------------------------------------------------------------')
                    terminate(
                        f'{self.SSA_STACK} deletion failed. Please resolve the issues, then rerun the script.',
                        ErrCode.EXCEPTION
                    )
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
        """
        Removes CloudFormation stack with option to retain resources.

        :param stack_id:            The name or the unique stack ID that's associated with the stack.
        :param retain_resources:    Tuple of logical IDs of the resources you want to retain.
                                    Applies for stack in the DELETE_FAILED state.
        :returns:                   Stack status.
        """
        stack_status = ''
        event_index = 0
        start_timestamp = datetime.now(timezone.utc)
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
            event_index = self._print_stack_events(stack_id=stack_id, pointer=event_index, start_date=start_timestamp)
            if in_progress: sleep(1)
        return stack_status

    def _print_stack_events(self, stack_id: str, pointer: int, start_date: datetime = None):
        """
        Prints stack events.

        :param stack_id:        Stack ID.
        :param pointer:         Indicates index of the first event to be printed.
        :param start_date:      If given, prints only events newer than the start_date.
        :returns:               Index of the last event + 1 (updated pointer, to be used in next iteration).
        """
        response = self._client.describe_stack_events(StackName=stack_id)
        stack_events = response['StackEvents']
        while "NextToken" in response:
            response = self._client.describe_stack_events(StackName=stack_id, NextToken=response["NextToken"])
            stack_events.extend(response['StackEvents'])
        stack_events = list(reversed(stack_events))
        if pointer >= len(stack_events):
            # no new events
            log_wait()
        else:
            for event in stack_events[pointer:]:
                timestamp = event.get('Timestamp', datetime(2000, 1, 1, tzinfo=timezone.utc))
                # no events newer than start_date
                if start_date and start_date >= timestamp:
                    continue
                # log new events
                timestamp = str(timestamp).split('.')[0].split('+')[0]
                logical_id = event.get('LogicalResourceId')
                status = event.get('ResourceStatus')
                status_reason = event.get('ResourceStatusReason')
                log_progress(f'[{timestamp}] \t{status}: {logical_id}')
                if 'FAIL' in status.upper():
                    log_error(f'{logical_id} resource status reason: {status_reason}')

        pointer = len(stack_events)
        return pointer
