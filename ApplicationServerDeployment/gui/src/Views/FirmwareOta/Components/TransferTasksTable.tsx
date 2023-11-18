import { Collapse, Table } from 'antd';
import { ITransferTask, TransferStatusType } from '../../../types';
import { ColumnsType } from 'antd/es/table';
import { useGetTransferTasks } from '../../../hooks/api/api';
import { TransferStatus } from '../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { Button, Flex } from 'antd';
import { CaretRightOutlined } from '@ant-design/icons';

export const TranserTasksTable = () => {
  const { data, isLoading } = useGetTransferTasks();

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
      title: 'Transfer End Time UTC',
      dataIndex: 'taskEndTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Duration'
    },
    {
      title: 'Filename',
      dataIndex: 'fileName'
    },
    {
      title: 'File Size',
      dataIndex: 'fileSizeKB'
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

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Tasks</h2>
        <Flex gap="small" align="center">
          <Button type="primary" size="middle" disabled={data?.transferTasks.length === 0}>
            Cancel Task
          </Button>
        </Flex>
      </Flex>
      <Table
        locale={{
          emptyText: (<div className='m-3 black'>No Tasks Created - Start a Firmware Update!</div>)
        }}
        rowSelection={{
          type: 'checkbox',
          onChange: (selectedRowKeys: React.Key[], selectedRows: ITransferTask[]) => {
            console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
          }
        }}
        columns={columns}
        dataSource={data?.transferTasks}
        rowKey={(item) => item.taskId}
        loading={isLoading}
      />
    </>
  );
};
