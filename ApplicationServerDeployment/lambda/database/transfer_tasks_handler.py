# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import boto3
import logging
import time

from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

from task import TransferTask

logger = logging.getLogger(__name__)


class TransferTasksHandler:
    """
    A class that provides read and write methods for the TransferTasks table.
    """

    TABLE_NAME = 'TransferTasks'

    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    # ----------------
    # Read operations
    # ----------------

    def get_all_transfer_tasks(self) -> [TransferTask]:
        """
        Gets all available records from the TransferTasks table.

        :return:    List of TransferTasks objects.
        """
        items = []
        try:
            response = self._table.scan()
            items.extend(response.get('Items', []))
            while "NextToken" in response:
                response = self._table.scan(NextToken=response["NextToken"])
                items.extend(response.get('Items', []))
        except ClientError as err:
            logger.error(f'Error while calling get_all_transfer_tasks: {err}')
            raise
        else:
            transferTasks = []
            for item in items:
                transferTask = TransferTask(**item)
                transferTasks.append(transferTask)
            return transferTasks

    def get_transfer_task_details(self, task_id: str) -> TransferTask:
        """
        Queries Measurements table for the records coming from given device withing a given time span.

        :param wireless_device_id:  taskId
        :return:                    task Detail
        """
        items = []
        try:
            filter_expression = Attr('task_id').eq(task_id)
            response = self._table.scan(IndexName='task_id', FilterExpression=filter_expression)
            items.extend(response.get('Items', []))
            while "NextToken" in response:
                response = self._table.scan(IndexName='task_id',
                                            FilterExpression=filter_expression,
                                            NextToken=response["NextToken"])
                items.extend(response.get('Items', []))
        except ClientError as err:
            logger.error(f'Error while calling get_device_transfer: {err}')
            raise
        else:
            return TransferTask(**items[0])


    # -----------------
    # Write operations
    # -----------------
    def add_transfer_task(self, transferTask: TransferTask):
        """
        Adds transferTask object to the TransferTasks table.

        :param taskId:  Task identifier.
        :return:             Updated TransferTask object.
        """
        try:
            self._table.put_item(
                Item={
                    'task_id': transferTask.get_task_id(),
                    'task_status': transferTask.get_task_status(),
                    'creation_time_UTC': transferTask.get_creation_time_UTC(),
                    'task_start_time_UTC': transferTask.get_task_start_time_UTC(),
                    'task_end_time_UTC': transferTask.get_task_end_time_UTC(),
                    'file_name': transferTask.get_file_name(),
                    'file_size_kb': transferTask.get_file_size_kb(),
                    'origination': transferTask.get_origination(),
                    'deviceIds': transferTask.get_deviceIds()
                },
                ReturnValues="ALL_OLD"
            )
        except ClientError as err:
            logger.error(
                f'Error while calling add_transfer_task for task_id: {transferTask.get_task_id()}: {err}'
            )
            raise
        else:
            return transferTask

