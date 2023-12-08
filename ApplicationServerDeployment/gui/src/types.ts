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
  wireless_devices: Array<IWirelessDevice>;
}

export type TransferStatusType = 'PENDING' | 'TRANSFERRING' | 'CANCELLED' | 'FAILED' | 'COMPLETE' | 'COMPLETED' | 'NONE';

export interface IWirelessDevice {
  device_id: string;
  transfer_status: TransferStatusType;
  status_updated_time_UTC: number;
  transfer_start_time_UTC: number;
  transfer_end_time_UTC: number;
  transfer_progress: number;
  file_name: string;
  file_size_kb: number;
  firmware_upgrade_status: 'Pending' | 'Completed' | 'Failed' | 'None';
  firmware_version: string;
  task_id: string;
}

export interface ITransferTask {
  task_id: string;
  task_status: TransferStatusType;
  creation_time_UTC: number;
  task_start_time_UTC: number;
  task_end_time_UTC: number;
  file_name: string;
  file_size_kb: number;
  origination: string;
  device_ids: Array<string>;
}

export interface ITransferTasks {
  transfer_tasks: Array<ITransferTask>;
}

export interface IFilenames {
  file_names: Array<string>;
}

export interface IStartTransferTask {
  file_name: string;
  start_time_UTC?: number;
  device_ids: Array<string>;
}

export interface ICancelTask {
  task_ids: Array<string>;
}

export interface IS3Files {
  file_names: Array<string>;
  current_firmware_file_name: string;
}

export interface ISetCurrentFirmware {
  filename: string;
}

export interface IWirelessDeviceStatus {
  device_id: string;
  status: TransferStatusType;
}