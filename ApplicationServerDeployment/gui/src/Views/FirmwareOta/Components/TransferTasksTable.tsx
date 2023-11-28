import { Collapse, Table, Button, Flex } from 'antd';
import { ITransferTask, TransferStatusType } from '../../../types';
import { useCancelTask, useGetTransferTasks } from '../../../hooks/api/api';
import { TransferStatus } from '../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { CaretRightOutlined } from '@ant-design/icons';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { getDurationString, getFileSize } from '../../../utils';
import { ColumnsType } from 'antd/es/table/interface';

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
      dataIndex: 'fileSizeKB',
      render: (value: number) => getFileSize(value)
    },
    {
      title: 'Origination',
      dataIndex: 'origination',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Progress'
    },
    {
      title: 'Devices',
      dataIndex: 'deviceIds',
      render: (list) => (
        <Collapse
          bordered={false}
          expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
          style={{ background: 'light-gray' }}
          items={[
            {
              key: '1',
              label: 'Completed: 0, Failed: 1, Transfering: 1',
              children: (
                <ul style={{ margin: 0 }}>
                  {list.map((value: string) => (
                    <li key={value}>{value}</li>
                  ))}
                </ul>
              ),
              style: {
                padding: 0
              }
            }
          ]}
        />
      )
    }
  ];

  const handleCancelTaskButtonClick = () => {
    cancelTask({ taskIds: tasksSelected });
  };

  const handleTasksSelected = (selectedRowKeys: React.Key[]) => {
    setTasksSelected(selectedRowKeys as Array<string>);
  };

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Tasks</h2>
        <Flex gap="small" align="center">
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
        loading={loadingTransferTasksList}
        pagination={{ pageSize: 10 }}
      />
    </>
  );
};
