// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export interface IDevice {
  button: number[];
  link_type: 'FSK' | 'BLE' | 'LoRa' | 'UNKNOWN';
  button_pressed: number[];
  time_to_live: number;
  last_uplink: number;
  led: number[];
  led_on: number[];
  sensor: boolean;
  sensor_unit: 'CELSIUS' | 'FAHRENHEIT' | 'UNKNOWN';
  wireless_device_id: string;
}

export interface IMeasurement {
  time: number;
  wireless_device_id: string;
  value: number;
}

export interface IWirelessDevices {
  wirelessDevices: Array<IWirelessDevice>;
}

export type TransferStatusType = 'PENDING' | 'TRANSFERRING' | 'CANCELLED' | 'FAILED' | 'COMPLETE' | 'COMPLETED' | 'NONE';

export interface IWirelessDevice {
  deviceId: string;
  transferStatus: TransferStatusType;
  statusUpdatedTimeUTC: number;
  transferStartTimeUTC: number;
  transferEndTimeUTC: number;
  transferProgress: number;
  fileName: string;
  fileSizeKb: number;
  firmwareUpgradeStatus: 'Pending' | 'Completed' | 'Failed' | 'None';
  firmwareVersion: string;
  taskId: string;
}

export interface ITransferTask {
  taskId: string;
  taskStatus: TransferStatusType;
  creationTimeUTC: number;
  taskStartTimeUTC: number;
  taskEndTimeUTC: number;
  fileName: string;
  fileSizeKb: number;
  origination: string;
  deviceIds: Array<string>;
}

export interface ITransferTasks {
  transferTasks: Array<ITransferTask>;
}

export interface IStartTransferTask {
  fileName: string;
  startTimeUTC?: number;
  deviceIds: Array<string>;
}

export interface ICancelTask {
  taskIds: Array<string>;
}

export interface IS3Files {
  fileNames: Array<string>;
  currentFirmwareFilename: string;
}

export interface ISetCurrentFirmware {
  filename: string;
}

export interface IWirelessDeviceStatus {
  deviceId: string;
  status: TransferStatusType;
}