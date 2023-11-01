// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export interface IDevice {
  button: number[];
  link_type: "FSK" | "BLE" | "LoRa" | "UNKNOWN";
  button_pressed: number[];
  time_to_live: number;
  last_uplink: number;
  led: number[];
  led_on: number[];
  sensor: boolean;
  sensor_unit: "CELSIUS" | "FAHRENHEIT" | "UNKNOWN";
  wireless_device_id: string;
}

export interface IMeasurement {
  time: number;
  wireless_device_id: string;
  value: number;
}

export interface IWirelessDevices {
  wirelesDevices: Array<IWirelessDevice>;
}

export type TransferStatusType =
  | "Pending"
  | "Transferring"
  | "Cancelled"
  | "Failed"
  | "Complete"
  | "Completed"
  | "None";

export interface IWirelessDevice {
  deviceId: string;
  transferStatus: TransferStatusType;
  statusUpdatedTimeUTC: number;
  transferEndTimeUTC: number;
  fileName: string;
  fileSizeKB: number;
  firmwareUpgradeStatus: "Pending" | "Completed" | "Failed" | "None";
  firmwareVersion: string;
}

export interface ITransferTasks {
  transferTasks: [
    {
      taskId: string;
      taskStatus: TransferStatusType;
      creationTimeUTC: number;
      taskEndTimeUTC: number;
      fileName: string;
      fileSizeKB: number;
      origination: string;
      deviceIds: ["String"];
    }
  ];
}
