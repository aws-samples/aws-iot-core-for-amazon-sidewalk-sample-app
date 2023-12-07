// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export const ENDPOINTS = {
  devices: '/devices',
  device: '/devices/:id',
  measurement: '/measurements/:id',
  led: '',
  login: '/auth',
  otaDevices: '/ota/deviceTransfers',
  otaTasks: '/ota/transferTasks',
  startTransferTasks: '/otaStart',
  cancelTransferTasks: '/otaCancel',
  s3Filenames: '/otaGetS3',
  upload: '/otaUpload',
  getDevicesByTaskId: '/otaDevices', // ?fuotaTaskId=val
  getDeviceById: '/ota/deviceTransfers/:id',
  setCurrentFirmware: '/otaSetCurrentFirmware'
};

export const interpolateParams = (route: string, params: { [k: string]: string }) => {
  let interpolatedRoute = route;
  Object.keys(params).forEach((key) => {
    interpolatedRoute = interpolatedRoute.replace(`:${key}`, params[key]);
  });
  return interpolatedRoute;
};
