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
    isLoading: loadingTransferTasksList,
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
      dataIndex: 'task_id'
    },
    {
      title: 'Status',
      dataIndex: 'task_status',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Creation Time UTC',
      dataIndex: 'creation_time_UTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Start Time UTC',
      dataIndex: 'task_start_time_UTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Duration',
      render: (_value: number, record: ITransferTask) =>
        getDurationString({ start: record.task_start_time_UTC, end: record.task_end_time_UTC })
    },
    {
      title: 'Filename',
      dataIndex: 'file_name'
    },
    {
      title: 'File Size',
      dataIndex: 'file_size_kb',
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
      dataIndex: 'device_ids',
      render: (list, record: ITransferTask) => <DevicesStatutes devices={list} taskId={record.task_id} />
    }
  ];

  const handleCancelTaskButtonClick = () => {
    cancelTask({ task_ids: tasksSelected });
  };

  const handleTasksSelected = (selectedRowKeys: React.Key[]) => {
    setTasksSelected(selectedRowKeys as Array<string>);
  };

  useEffect(() => {
    if (!transferTaskList) return;

    scrollManager.setItemsDisposition(transferTaskList, 'tasks');
  }, [transferTaskList?.transfer_tasks.length]);

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Tasks</h2>
        <Flex gap="small" align="center">
          <Button
            onClick={() => refetchTransferTasks()}
            loading={loadingTransferTasksList}
            disabled={loadingTransferTasksList}
            aria-label="reload table"
          >
            <ReloadOutlined />
          </Button>
          <Button
            type="primary"
            size="middle"
            disabled={cancelingTask || transferTaskList?.transfer_tasks.length === 0 || tasksSelected.length === 0}
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
        dataSource={transferTaskList?.transfer_tasks}
        rowKey={(item) => item.task_id}
        loading={loadingTransferTasksList}
        pagination={{
          pageSize: scrollManager.tables.tasks.pageSize,
          current: scrollManager.pageIndex.tasks,
          onChange: (page) => scrollManager.setPageIndex(page, 'tasks')
        }}
      />
    </>
  );
};
