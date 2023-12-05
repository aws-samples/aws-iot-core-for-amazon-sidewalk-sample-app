import { DatePicker, Select, Table, Upload, Button, Flex, DatePickerProps } from 'antd';
import { IStartTransferTask, IWirelessDevice, TransferStatusType } from '../../../types';
import { ColumnsType } from 'antd/es/table';
import {
  useGetFileNames,
  useGetWirelessDevices,
  useS3Upload,
  useStartTransferTask
} from '../../../hooks/api/api';
import { UploadOutlined } from '@ant-design/icons';
import { TransferStatus } from '../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import dayjs from 'dayjs';
import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { getDurationString, getFileSize, showValueOrDash, verifyAuth } from '../../../utils';
import { RcFile } from 'antd/es/upload/interface';
import { apiClient } from '../../../apiClient';
import { ENDPOINTS, interpolateParams } from '../../../endpoints';
import { AxiosError } from 'axios';
import { APP_CONFIG } from '../../../appConfig';

export const WirelessDevicesTable = () => {
  const [_, forceRender] = useState({});
  const [startTransferTaskPayload, setStartTransferTaskPayload] = useState<IStartTransferTask>({
    fileName: '',
    startTimeUTC: undefined,
    deviceIds: []
  });

  const { data: devicesList, isLoading: isLoadingDevices, refetch: refetchWirelessDevices } = useGetWirelessDevices();
  const { mutate: upload, isLoading: isUploading } = useS3Upload({
    onSuccess: (_, file: {}) => {
      toast.success('File Uploaded');
      lastItemUploaded.current = (file as RcFile).name;
      // s3List?.push((file as RcFile).name);

      refetchFilenames();
    }
  });
  const { data: s3List, isLoading: isLoadingFilenames, refetch: refetchFilenames } = useGetFileNames();
  const { mutate: startTransferTask, isLoading: isTransfering } = useStartTransferTask({
    onSuccess: () => {
      toast.success('Task transferred');
      setStartTransferTaskPayload({ deviceIds: [], fileName: '', startTimeUTC: undefined });
      refetchWirelessDevices();
    }
  });

  const lastItemUploaded = useRef('');
  const wirelessDevicesIntervalRefs = useRef<{ [key: string]: string | number }>({});
  const mockProgressCounter = useRef<{ [key: string]: number }>({});

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
      title: 'Transfer Progress',
      dataIndex: 'transferProgress',
      render: (value: number) => (value ? `${value}%` : `${showValueOrDash(value)}`)
    },
    {
      title: 'Status Updated UTC',
      dataIndex: 'statusUpdatedTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Start Time UTC',
      dataIndex: 'transferStartTimeUTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Duration',
      render: (_value: number, record: IWirelessDevice) => {
        // check if 'end' should be update time
        return getDurationString({ start: record.transferStartTimeUTC, end: record.transferEndTimeUTC || Date.now() })
      }
    },
    {
      title: 'Filename',
      dataIndex: 'fileName'
    },
    {
      title: 'Size',
      dataIndex: 'fileSizeKB',
      render: (value: number) => getFileSize(value)
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

  const handleUpload = (file: RcFile) => {
    const isGreaterThan1M = file.size / 1024 / 1024 > 1;
    if (isGreaterThan1M) {
      return toast.error("File's size should be less than 1MB");
    }
    upload(file);
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

  const fetchDeviceByIdAndMutate = async (id: string) => {
    try {
      const result = await apiClient.get<IWirelessDevice>(interpolateParams(ENDPOINTS.getDeviceById, { id }));
      const individualDevice = result.data;

      const deviceToReplace = devicesList?.wirelessDevices.find((device) => device.deviceId === individualDevice.deviceId);

      // mutate individual wireless data and force render
      Object.keys(deviceToReplace!).forEach((key) => {
        // @ts-ignore
        deviceToReplace[key] = individualDevice[key];
      });
      forceRender({});

      // should keep fetching while...
      return individualDevice.transferProgress !== 100;
    } catch (error) {
      verifyAuth((error as AxiosError)?.response?.status || 500);
      toast.error('Erros while getting device by id');
      return false;
    }
  };

  useEffect(() => {
    const newItemUploaded = s3List?.find((filename) => filename === lastItemUploaded.current);

    if (newItemUploaded) {
      handleFilenameSelected(newItemUploaded);
    }
  }, [s3List?.length]);

  // POLLING INDIVIDUAL DEVICE LOGIC
  useEffect(() => {
    if (!devicesList) return;
    const devicesToPoll = devicesList?.wirelessDevices.filter(
      (device) => device.transferStatus === 'TRANSFERRING' || device.transferStatus === 'PENDING'
    );

    if (devicesToPoll?.length === 0) return;

    for (const device of devicesToPoll!) {
      mockProgressCounter.current[device.deviceId] = 1;
      wirelessDevicesIntervalRefs.current[device.deviceId] = window.setInterval(async () => {
        // mocklogic
        const shouldKeepFetching = await fetchDeviceByIdAndMutate(
          `${device.deviceId}_${mockProgressCounter.current[device.deviceId]}`
        );

        if (!shouldKeepFetching) {
          window.clearInterval(wirelessDevicesIntervalRefs.current[device.deviceId] as number);
          mockProgressCounter.current[device.deviceId] = 1;
        }

        // mock logic
        mockProgressCounter.current[device.deviceId] += 1;
      }, APP_CONFIG.intervals.otaProgressTasks);
    }
  }, [devicesList]);

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Devices</h2>
        <Flex gap="small" align="center">
          <Upload beforeUpload={handleUpload} showUploadList={false} disabled={isUploading} accept=".bin,.hex,.nvm3,.s37">
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
            options={s3List?.map((filename) => ({ label: filename, value: filename }))}
            value={startTransferTaskPayload.fileName}
          />
          <DatePicker
            showTime
            placeholder="Now"
            onChange={handleDatePickerChange}
            format="YYYY-MM-DD HH:mm:ss"
            disabledDate={disabledDate}
            disabledTime={disabledDateTime}
            value={startTransferTaskPayload.startTimeUTC ? dayjs(startTransferTaskPayload.startTimeUTC) : undefined}
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
        dataSource={devicesList?.wirelessDevices}
        rowKey={(item) => item.deviceId}
        loading={isLoadingDevices}
        pagination={{ pageSize: 10 }}
      />
    </>
  );
};
