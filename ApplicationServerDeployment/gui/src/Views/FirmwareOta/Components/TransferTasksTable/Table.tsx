// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Table, Button, Flex } from 'antd';
import { ITransferTask, TransferStatusType } from '../../../../types';
import { useCancelTask, useGetTransferTasks } from '../../../../hooks/api/api';
import { TransferStatus } from '../../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { getDurationString, getFileSize } from '../../../../utils';
import { ColumnsType } from 'antd/es/table/interface';
import { useRowScroller } from '../ScrollManager';
import { DevicesStatutes } from './DevicesStatuses';
import { ReloadOutlined } from '@ant-design/icons';

export const TranserTasksTable = () => {
  const {
    data: transferTaskList,
    isLoading: isLoadingTransferTasksList,
    isRefetching: isRefetchingTransferTasksList,
    refetch: refetchTransferTasks
  } = useGetTransferTasks();
  const { mutate: cancelTask, isLoading: cancelingTask } = useCancelTask({
    onSuccess: () => {
      toast.success('Tasks cancelled');
      setTasksSelected([]);
      refetchTransferTasks();
    }
  });
  const [tasksSelected, setTasksSelected] = useState([] as Array<string>);
  const scrollManager = useRowScroller();

  const columns: ColumnsType<ITransferTask> = [
    {
      title: 'Task Id',
      dataIndex: 'taskId'
    },
    {
      title: 'Status',
      dataIndex: 'taskStatus',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Creation Time UTC',
      dataIndex: 'creationTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Start Time UTC',
      dataIndex: 'taskStartTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Duration',
      render: (_value: number, record: ITransferTask) =>
        getDurationString({ start: record.taskStartTimeUTC, end: record.taskEndTimeUTC })
    },
    {
      title: 'Filename',
      dataIndex: 'fileName'
    },
    {
      title: 'File Size',
      dataIndex: 'fileSizeKb',
      render: (value: number) => getFileSize(value)
    },
    {
      title: 'Origination',
      dataIndex: 'origination',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Progress',
      className: 'progress-task-id'
    },
    {
      title: 'Devices',
      dataIndex: 'deviceIds',
      render: (list, record: ITransferTask) => (
        <DevicesStatutes devices={list} taskId={record.taskId} forceRefetching={isRefetchingTransferTasksList} />
      )
    }
  ];

  const handleCancelTaskButtonClick = () => {
    cancelTask({ taskIds: tasksSelected });
  };

  const handleTasksSelected = (selectedRowKeys: React.Key[]) => {
    setTasksSelected(selectedRowKeys as Array<string>);
  };

  useEffect(() => {
    if (!transferTaskList) return;

    scrollManager.setItemsDisposition(transferTaskList, 'tasks');
  }, [transferTaskList?.transferTasks.length]);

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Tasks</h2>
        <Flex gap="small" align="center">
          <Button
            onClick={() => refetchTransferTasks()}
            loading={isLoadingTransferTasksList}
            disabled={isLoadingTransferTasksList}
            aria-label="reload table"
          >
            <ReloadOutlined />
          </Button>
          <Button
            type="primary"
            size="middle"
            disabled={cancelingTask || transferTaskList?.transferTasks.length === 0 || tasksSelected.length === 0}
            onClick={handleCancelTaskButtonClick}
            loading={cancelingTask}
          >
            {cancelingTask ? 'Cancelling task' : 'Cancel Task'}
          </Button>
        </Flex>
      </Flex>
      <Table
        locale={{
          emptyText: <div className="m-3 black">No Tasks Created - Start a Firmware Update!</div>
        }}
        rowSelection={{
          type: 'checkbox',
          onChange: handleTasksSelected,
          selectedRowKeys: tasksSelected
        }}
        columns={columns}
        dataSource={transferTaskList?.transferTasks}
        rowKey={(item) => item.taskId}
        loading={isRefetchingTransferTasksList || isLoadingTransferTasksList}
        pagination={{
          pageSize: scrollManager.tables.tasks.pageSize,
          current: scrollManager.pageIndex.tasks,
          onChange: (page) => scrollManager.setPageIndex(page, 'tasks')
        }}
      />
    </>
  );
};
