import { DatePicker, DatePickerProps, Select, Table, Upload } from 'antd';
import { IStartTransferTask, IWirelessDevice, TransferStatusType } from '../../../types';
import { ColumnsType } from 'antd/es/table';
import { useGetFileNames, useGetWirelessDevices, useS3Upload, useStartTransferTask } from '../../../hooks/api/api';
import { UploadOutlined } from '@ant-design/icons';
import { TransferStatus } from '../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { Button, Flex } from 'antd';
import { UploadChangeParam, UploadFile } from 'antd/es/upload';
import dayjs from 'dayjs';
import { useState } from 'react';
import toast from 'react-hot-toast';

export const WirelessDevicesTable = () => {
  const [startTransferTaskPayload, setStartTransferTaskPayload] = useState<IStartTransferTask>({
    fileName: '',
    startTimeUTC: undefined,
    deviceIds: []
  });

  const { data: devicesList, isLoading: isLoadingDevices } = useGetWirelessDevices();
  const { mutate: upload, isLoading: isUploading } = useS3Upload();
  const { data: s3List, isLoading: isLoadingFilenames, refetch: refetchFilenames } = useGetFileNames();
  const { mutate: startTransferTask, isLoading: isTransfering } = useStartTransferTask({
    onSuccess: () => {
      toast.success('Task transferred');
      setStartTransferTaskPayload((prevState) => ({ ...prevState, deviceIds: [] }));
    }
  });

  const columns: ColumnsType<IWirelessDevice> = [
    {
      title: 'Device Id',
      dataIndex: 'deviceId'
    },
    {
      title: 'Transfer Status',
      dataIndex: 'transferStatus',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Status Updated UTC',
      dataIndex: 'statusUpdatedTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Transfer End Time UTC',
      dataIndex: 'transferEndTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Filename',
      dataIndex: 'fileName'
    },
    {
      title: 'Size',
      dataIndex: 'fileSizeKB'
    },
    {
      title: 'Firmware Upgrade Status',
      dataIndex: 'firmwareUpgradeStatus',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Firmware Version',
      dataIndex: 'firmwareVersion'
    }
  ];

  const handleDatePickerChange = (value: DatePickerProps['value']) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, startTimeUTC: value?.valueOf() }));
  };

  const range = (start: number, end: number) => {
    const result = [];
    for (let i = start; i < end; i++) {
      result.push(i);
    }
    return result;
  };

  const disabledDateTime = () => ({
    disabledHours: () => range(0, 24).splice(0, dayjs().hour()),
    disabledMinutes: () => range(0, 60).splice(0, dayjs().minute()),
    disabledSeconds: () => range(0, 60).splice(0, dayjs().second())
  });

  const disabledDate = (current: dayjs.Dayjs) => {
    // Can not select days before today and now
    return current && current < dayjs().startOf('day');
  };

  const filterOption = (input: string, option?: { label: string; value: string }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase());

  const handleUpload = async (param: UploadChangeParam<UploadFile<any>>) => {
    await upload(param.file);
    refetchFilenames();
  };

  const handleFilenameSelected = (fileName: string) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, fileName }));
  };

  const handleDeviceSelected = (selectedRowKeys: React.Key[]) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, deviceIds: selectedRowKeys as Array<string> }));
  };

  const canStartTrasnferTask = startTransferTaskPayload.fileName.length > 0 && startTransferTaskPayload.deviceIds.length > 0;

  const handleStarTransferTask = () => {
    startTransferTask(startTransferTaskPayload);
  };

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Devices</h2>
        <Flex gap="small" align="center">
          <Upload onChange={handleUpload} showUploadList={false} disabled={isUploading}>
            <Button loading={isUploading} icon={<UploadOutlined />}>
              {isUploading ? 'Uploading' : 'Upload file'}
            </Button>
          </Upload>
          <Select
            showSearch
            placeholder="Select a file"
            optionFilterProp="children"
            onChange={handleFilenameSelected}
            style={{ minWidth: '200px' }}
            loading={isLoadingFilenames}
            disabled={isLoadingFilenames}
            filterOption={filterOption}
            options={s3List?.fileNames?.map((filename) => ({ label: filename, value: filename }))}
          />
          <DatePicker
            showTime
            placeholder="Now"
            onChange={handleDatePickerChange}
            format="YYYY-MM-DD HH:mm:ss"
            disabledDate={disabledDate}
            disabledTime={disabledDateTime}
          />
          <Button
            type="primary"
            size="middle"
            disabled={!canStartTrasnferTask}
            onClick={handleStarTransferTask}
            loading={isTransfering}
          >
            Update Firmware
          </Button>
        </Flex>
      </Flex>
      <Table
        locale={{
          emptyText: <div className="m-3 black">No Wireless devices detected</div>
        }}
        rowSelection={{
          type: 'checkbox',
          onChange: handleDeviceSelected,
          selectedRowKeys: startTransferTaskPayload.deviceIds
        }}
        columns={columns}
        dataSource={devicesList?.wirelesDevices}
        rowKey={(item) => item.deviceId}
        loading={isLoadingDevices}
      />
    </>
  );
};
