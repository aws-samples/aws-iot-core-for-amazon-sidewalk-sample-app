# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from typing import List

import boto3
import logging
import time

from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Attr
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from task import TransferTask

logger = logging.getLogger(__name__)


class TransferTasksHandler:
    """
    A class that provides read and write methods for the TransferTasks table.
    """

    TABLE_NAME = 'TransferTasks'
    PRIMARY_KEY = 'task_id'
    client = boto3.client('dynamodb')
    
    def __init__(self):
        self._table = boto3.resource('dynamodb').Table(self.TABLE_NAME)

    # ----------------
    # Read operations
    # ----------------

    def get_all_transfer_tasks(self) -> List[TransferTask]:
        """
        Gets all available records from the TransferTasks table.

        :return:    List of TransferTasks objects.
        """
        try:
            response = self._table.scan()
            items = response.get('Items', [])

            for item in items:
                yield TransferTask(**item)

            while "LastEvaluatedKey" in response:
                response = self._table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
                items = response.get('Items', [])

                for item in items:
                    yield TransferTask(**item)

        except ClientError as err:
            logger.error(f'Error while calling get_all_transfer_tasks: {err}', exc_info=True)
            raise

    def get_transfer_task_details(self, taskId: str) -> TransferTask:
        """
        Queries Measurements table for the records coming from given device withing a given time span.

        :param task id:  taskId
        :return:                    task Detail
        """
        items = []
        try:
            response = self._table.query(KeyConditionExpression=Key('task_id').eq(taskId))
            items = response.get('Items', [])
        except ClientError as err:
            logger.error(f'Error while calling get_transfer_task_details: {err}')
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
                    'device_ids': transferTask.get_device_ids()
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
        

    # -----------------
    # Update operations
    # -----------------
    def update_transfer_task(self, transferTask: TransferTask):
        """
        Updates transferTask object to the TransferTasks table.

        :param taskId:  Task identifier.
        :return:             Updated TransferTask object.
        """
        try:
            self._table.put_item(Item=transferTask.to_dict())
        except ClientError as err:
            logger.error(
                f'Error while calling update_transfer_task for task_id: {transferTask.get_task_id()}: {err}'
            )
            raise
        else:
            return transferTask

    # -----------------
    # Batch Update operations
    # -----------------
    def batch_update_transfer_task(self, transferTasks):
        """
        Updates transferTask object to the TransferTasks table.

        :param taskId:  Task identifier.
        :return:             Updated TransferTask object.
        """
        unprocessed_items = []
        try:
            # Prepare the batch write request
            print('Batch write ', transferTasks)
            batch_write_request = []
            for task in transferTasks:
                update_request = {
                    'PutRequest': {
                        'Item': task
                    }
                }
                batch_write_request.append(update_request)

            # Perform the batch write
            response = self.client.batch_write_item(RequestItems={self.TABLE_NAME: batch_write_request})

            # Check for unprocessed items
            unprocessed_items = response.get('UnprocessedItems', {})
            while unprocessed_items:
                response = self.client.batch_write_item(RequestItems=unprocessed_items)
                unprocessed_items = response.get('UnprocessedItems', {})
        except ClientError as err:
            logger.error(
                f'Error while calling update_transfer_task for tasks: {transferTasks}: {err}'
            )
            raise
        else:
            return unprocessed_items
        

    # -----------------
    # Batch Get operations
    # -----------------
    def get_transfer_tasks(self, task_ids):
        """
        Updates transferTask object to the TransferTasks table.

        :param taskId:  Task identifier.
        :return:             Updated TransferTask object.
        """
        try:
            # Prepare the batch write request
            keys_to_get = [{self.PRIMARY_KEY: {'S': task_id}} for task_id in task_ids]

            # Prepare the batch get request
            batch_get_request = {
                self.TABLE_NAME: {
                    'Keys': keys_to_get
                }
            }

            # Perform the batch get
            response = self.client.batch_get_item(RequestItems=batch_get_request)

            # Retrieve the items from the response
            items = response.get('Responses', {}).get(self.TABLE_NAME, [])

            # Print the retrieved items
            for item in items:
                print("Retrieved Item:", item)
            converted_items = [{attr: list(value.values())[0] for attr, value in item.items()} for item in items]
            print('converted items ', converted_items)
            
        except ClientError as err:
            logger.error(
                f'Error while calling get_transfer_tasks for tasks: {task_ids}: {err}'
            )
            raise
        else:
            return converted_items
        
    # -----------------
    # Batch Get operations
    # -----------------
    def get_transfer_tasks(self, task_ids):
        """
        Updates transferTask object to the TransferTasks table.

        :param taskId:  Task identifier.
        :return:             Updated TransferTask object.
        """
        items = []
        try:
            # Prepare the batch write request
            keys_to_get = [{self.PRIMARY_KEY: {'S': task_id}} for task_id in task_ids]

            # Prepare the batch get request
            batch_get_request = {
                self.TABLE_NAME: {
                    'Keys': keys_to_get
                }
            }

            # Perform the batch get
            response = self.client.batch_get_item(RequestItems=batch_get_request)

            # Retrieve the items from the response
            ddb_items = response.get('Responses', {}).get(self.TABLE_NAME, [])

            # Print the retrieved items
            for item in ddb_items:
                print("Retrieved Item:", item)
            items = [dynamo_obj_to_python_obj(item) for item in ddb_items]
        except ClientError as err:
            logger.error(
                f'Error while calling get_transfer_tasks for tasks: {task_ids}: {err}'
            )
            raise
        else:
            return items


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  

