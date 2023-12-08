import { Select, Table, Upload, Button, Flex, DatePickerProps } from 'antd';
import { IStartTransferTask, IWirelessDevice, TransferStatusType } from '../../../../types';
import { ColumnsType } from 'antd/es/table';
import { useGetFileNames, useGetWirelessDevices, useS3Upload, useStartTransferTask } from '../../../../hooks/api/api';
import { UploadOutlined } from '@ant-design/icons';
import { TransferStatus } from '../../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { getDurationString, getFileSize, showValueOrDash, verifyAuth } from '../../../../utils';
import { RcFile } from 'antd/es/upload/interface';
import { apiClient } from '../../../../apiClient';
import { ENDPOINTS, interpolateParams } from '../../../../endpoints';
import { AxiosError } from 'axios';
import { DatePicker } from './DatePicker';
import { useRowScroller } from '../ScrollManager';
import { APP_CONFIG } from '../../../../appConfig';
import { MOCK_MODE } from '../../../../constants';
import { ReloadOutlined } from '@ant-design/icons';

export const WirelessDevicesTable = () => {
  const [_, forceRender] = useState({});

  const [startTransferTaskPayload, setStartTransferTaskPayload] = useState<IStartTransferTask>({
    file_name: '',
    start_time_UTC: undefined,
    device_ids: []
  });

  const { data: devicesList, isLoading: isLoadingDevices, refetch: refetchWirelessDevices } = useGetWirelessDevices();
  const { mutate: upload, isLoading: isUploading } = useS3Upload({
    onSuccess: (_, file: {}) => {
      toast.success('File Uploaded');
      lastItemUploaded.current = (file as RcFile).name;

      refetchFilenames();
    }
  });
  const { data: s3List, isLoading: isLoadingFilenames, refetch: refetchFilenames } = useGetFileNames();
  const { mutate: startTransferTask, isLoading: isTransfering } = useStartTransferTask({
    onSuccess: () => {
      toast.success('Task transferred');
      setStartTransferTaskPayload({ device_ids: [], file_name: '', start_time_UTC: undefined });
      refetchWirelessDevices();
    }
  });
  const scrollManager = useRowScroller();

  const lastItemUploaded = useRef('');
  const wirelessDevicesIntervalRefs = useRef<{ [key: string]: string | number }>({});
  const mockProgressCounter = useRef<{ [key: string]: number }>({});
  const canStartTrasnferTask =
    startTransferTaskPayload.file_name.length > 0 && startTransferTaskPayload.device_ids.length > 0;

  const columns: ColumnsType<IWirelessDevice> = [
    {
      title: 'Device Id',
      dataIndex: 'device_id'
    },
    {
      title: 'Transfer Status',
      dataIndex: 'transfer_status',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Transfer Progress',
      dataIndex: 'transfer_progress',
      render: (value: number) => (value ? `${value}%` : `${showValueOrDash(value)}`)
    },
    {
      title: 'Status Updated UTC',
      dataIndex: 'status_updated_time_UTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Start Time UTC',
      dataIndex: 'transfer_start_time_UTC',
      render: (value: number) => <>{format(new Date(value), 'MM/dd/yyyy HH:mm:ss')}</>
    },
    {
      title: 'Duration',
      render: (_value: number, record: IWirelessDevice) => {
        return getDurationString({
          start: record.transfer_start_time_UTC,
          end: record.transfer_end_time_UTC || record.status_updated_time_UTC
        });
      }
    },
    {
      title: 'Filename',
      dataIndex: 'file_name'
    },
    {
      title: 'Size',
      dataIndex: 'file_size_kb',
      render: (value: number) => getFileSize(value)
    },
    {
      title: 'Firmware Upgrade Status',
      dataIndex: 'firmware_upgrade_status',
      render: (value: TransferStatusType) => <TransferStatus type={value} />
    },
    {
      title: 'Firmware Version',
      dataIndex: 'firmware_version'
    },
    {
      title: 'Task ID',
      dataIndex: 'task_id',
      render: (value: string) => <a onClick={() => scrollManager.scrollTo(value, 'tasks')}>{showValueOrDash(value)}</a>
    }
  ];

  const handleDatePickerChange = (value: DatePickerProps['value']) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, start_time_UTC: value?.valueOf() }));
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

  const handleFilenameSelected = (file_name: string) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, file_name }));
  };

  const handleDeviceSelected = (selectedRowKeys: React.Key[]) => {
    setStartTransferTaskPayload((prevState) => ({ ...prevState, device_ids: selectedRowKeys as Array<string> }));
  };

  const handleStarTransferTask = () => {
    startTransferTask(startTransferTaskPayload);
  };

  const fetchDeviceByIdAndMutate = async (id: string) => {
    try {
      const result = await apiClient.get<IWirelessDevice>(interpolateParams(ENDPOINTS.getDeviceById, { id }));
      const individualDevice = result.data;

      const deviceToReplace = devicesList?.wireless_devices.find(
        (device) => device.device_id === individualDevice.device_id
      );

      // mutate individual wireless data and force render
      Object.keys(deviceToReplace!).forEach((key) => {
        // @ts-ignore
        deviceToReplace[key] = individualDevice[key];
      });
      forceRender({});

      // should keep fetching while...
      return individualDevice.transfer_progress !== 100;
    } catch (error) {
      verifyAuth((error as AxiosError)?.response?.status || 500);
      toast.error(`Error while getting device by id: ${id}`);

      // polling stops...
      return false;
    }
  };

  useEffect(() => {
    const newItemUploaded = s3List?.file_names.find((filename) => filename === lastItemUploaded.current);

    if (newItemUploaded) {
      handleFilenameSelected(newItemUploaded);
    }
  }, [s3List?.file_names.length]);

  // POLLING INDIVIDUAL DEVICE LOGIC
  useEffect(() => {
    if (!devicesList) return;
    const devicesToPoll = devicesList?.wireless_devices.filter(
      (device) => device.transfer_status === 'TRANSFERRING' || device.transfer_status === 'PENDING'
    );

    if (devicesToPoll?.length === 0) return;

    if (MOCK_MODE) {
      // JUST LOGIC FOR MOCKING POLLING
      for (const device of devicesToPoll!) {
        mockProgressCounter.current[device.device_id] = 1;
        wirelessDevicesIntervalRefs.current[device.device_id] = window.setInterval(async () => {
          // mocklogic
          const shouldKeepFetching = await fetchDeviceByIdAndMutate(
            `${device.device_id}_${mockProgressCounter.current[device.device_id]}`
          );

          if (!shouldKeepFetching) {
            window.clearInterval(wirelessDevicesIntervalRefs.current[device.device_id] as number);
            // mocklogic
            mockProgressCounter.current[device.device_id] = 1;
          }

          // mock logic
          mockProgressCounter.current[device.device_id] += 1;
        }, APP_CONFIG.intervals.otaProgressTasks);
      }
    } else {
      for (const device of devicesToPoll!) {
        wirelessDevicesIntervalRefs.current[device.device_id] = window.setInterval(async () => {
          const shouldKeepFetching = await fetchDeviceByIdAndMutate(device.device_id);

          if (!shouldKeepFetching) {
            window.clearInterval(wirelessDevicesIntervalRefs.current[device.device_id] as number);
          }
        }, APP_CONFIG.intervals.otaProgressTasks);
      }
    }

    return () => {
      devicesToPoll.forEach((device) => {
        window.clearInterval(wirelessDevicesIntervalRefs.current[device.device_id] as number);
      });
    };
  }, [devicesList]);

  useEffect(() => {
    if (!devicesList) return;

    scrollManager.setItemsDisposition(devicesList, 'devices');
  }, [devicesList?.wireless_devices.length]);

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Devices</h2>
        <Flex gap="small" align="center">
          <Button onClick={() => refetchWirelessDevices()} loading={isLoadingDevices} disabled={isLoadingDevices}>
            <ReloadOutlined />
          </Button>
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
            options={s3List?.file_names.map((filename) => ({ label: filename, value: filename }))}
            value={startTransferTaskPayload.file_name}
          />
          <DatePicker dateValue={startTransferTaskPayload.start_time_UTC} onDatePickerChange={handleDatePickerChange} />
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
          selectedRowKeys: startTransferTaskPayload.device_ids
        }}
        columns={columns}
        dataSource={devicesList?.wireless_devices}
        rowKey={(item) => item.device_id}
        loading={isLoadingDevices}
        pagination={{
          pageSize: scrollManager.tables.devices.pageSize,
          current: scrollManager.pageIndex.devices,
          onChange: (page) => scrollManager.setPageIndex(page, 'devices')
        }}
        scroll={{ x: 'max-content' }}
      />
    </>
  );
};
