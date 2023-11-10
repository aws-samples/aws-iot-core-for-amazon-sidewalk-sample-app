import { DatePicker, DatePickerProps, MenuProps, Space, Table, Upload } from 'antd';
import { IWirelessDevice, TransferStatusType } from '../../../types';
import { ColumnsType } from 'antd/es/table';
import { useGetWirelessDevices } from '../../../hooks/api/api';
import { UploadOutlined } from '@ant-design/icons';
import { TransferStatus } from '../../../components/TransferStatus/TransferStatus';
import { format } from 'date-fns';
import { Button, Dropdown, Flex } from 'antd';

export const WirelessDevicesTable = () => {
  const { data, isLoading } = useGetWirelessDevices();

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

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    console.log('click', e);
  };

  const ddItems: MenuProps['items'] = [
    {
      label: '1st menu item',
      key: '1'
    },
    {
      label: '2nd menu item',
      key: '2'
    },
    {
      label: '3rd menu item',
      key: '3',
      danger: true
    },
    {
      label: '4rd menu item',
      key: '4',
      danger: true,
      disabled: true
    }
  ];

  const menuProps = {
    items: ddItems,
    onClick: handleMenuClick
  };

  const onDatePickerChange = (value: DatePickerProps['value'], dateString: [string, string] | string) => {
    console.log('Selected Time: ', value);
    console.log('Formatted Selected Time: ', dateString);
  };

  return (
    <>
      <Flex gap="small" wrap="wrap" justify="space-between">
        <h2>Devices</h2>
        <Flex gap="small" align="center">
          <Upload>
            <Button icon={<UploadOutlined />}>Upload file</Button>
          </Upload>
          <Space wrap>
            <Dropdown.Button menu={menuProps}>File selected</Dropdown.Button>
          </Space>
          <DatePicker showTime onChange={onDatePickerChange} />
          <Button type="primary" size="middle">
            Update Firmware
          </Button>
        </Flex>
      </Flex>
      <Table
        rowSelection={{
          type: 'checkbox',
          onChange: (selectedRowKeys: React.Key[], selectedRows: IWirelessDevice[]) => {
            console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
          }
        }}
        columns={columns}
        dataSource={data?.wirelesDevices}
        rowKey={item => item.deviceId}
        loading={isLoading}
      />
    </>
  );
};
