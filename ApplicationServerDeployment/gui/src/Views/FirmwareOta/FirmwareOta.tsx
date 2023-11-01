import { useGetWirelessDevices } from "../../hooks/api/api";
import { Table } from "antd";
import { IWirelessDevice, StatusType } from "../../types";
import { ColumnsType } from "antd/es/table";
import { format } from "date-fns";
import styles from "./styles.module.css";
import classNames from "classnames";
import { TransferStatus } from "../../components/TransferStatus/TransferStatus";

export const FirmwareOta = () => {
  const { data, isLoading } = useGetWirelessDevices();

  const columns: ColumnsType<IWirelessDevice> = [
    {
      title: "Device Id",
      dataIndex: "deviceId",
    },
    {
      title: "Transfer Status",
      dataIndex: "transferStatus",
      render: (value: StatusType) => <TransferStatus type={value} />
    },
    {
      title: "Status Updated UTC",
      dataIndex: "statusUpdatedTimeUTC",
      render: (value: number) => (
        <>{format(new Date(value), "MM/dd/yyyy HH:mm:ss")}</>
      ),
    },
    {
      title: "Transfer End Time UTC",
      dataIndex: "transferEndTimeUTC",
      render: (value: number) => (
        <>{format(new Date(value), "MM/dd/yyyy HH:mm:ss")}</>
      ),
    },
    {
      title: "Filename",
      dataIndex: "fileName",
    },
    {
      title: "Size",
      dataIndex: "fileSizeKB",
    },
    {
      title: "Firmware Upgrade Status",
      dataIndex: "firmwareUpgradeStatus",
      render: (value: StatusType) => <TransferStatus type={value} />
    },
    {
      title: "Firmware Version",
      dataIndex: "firmwareVersion",
    },
  ];

  return (
    <div className="p-3">
      <h2 className={classNames(styles.colorBlack, 'pl-3')}>Instructions</h2>
      <ul className={classNames(styles.colorBlack, 'mb-3')}>
        <li>
          Click <b>Upload File</b> to upload a file, it will be stored in an S3
          bucket that the File Transfer App can pull from
        </li>
        <li>
          <b>Select a file</b> from the drop down you want to transfer to one or
          more devices
        </li>
        <li>
          Check the box to <b>select all the devices</b> you want to transfer
          the file to
        </li>
        <li>
          If you want to schedule the Task in the future{" "}
          <b>select a Start Time</b>, this will default to NOW if not selected
        </li>
        <li>
          Click <b>Transfer</b> to create a Task and start transferring the
          selected file to the selected devices
        </li>
        <li>
          Clicking <b>Transfer</b> again will create a new Task for any selected
          device not in Transferring status
        </li>
        <li>
          Clicking <b>Cancel</b> in the Task table will terminate all
          Transferring tasks that are selected, all devices in the task will be
          Canceled
        </li>
      </ul>
      <Table
        rowSelection={{
          type: "checkbox",
          onChange: (
            selectedRowKeys: React.Key[],
            selectedRows: IWirelessDevice[]
          ) => {
            console.log(
              `selectedRowKeys: ${selectedRowKeys}`,
              "selectedRows: ",
              selectedRows
            );
          },
        }}
        columns={columns}
        dataSource={data?.wirelesDevices}
        loading={isLoading}
      />
    </div>
  );
};
