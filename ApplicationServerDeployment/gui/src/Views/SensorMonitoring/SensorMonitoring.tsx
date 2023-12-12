// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useEffect, useRef, useState } from 'react';
import { apiClient } from '../../apiClient';
import { APP_CONFIG } from '../../appConfig';
import { ENDPOINTS } from '../../endpoints';
import { IDevice } from '../../types';
import { logger } from '../../utils/logger';
import { Device } from '../../components/Device/Device';
import { Spinner } from '../../components/Spinner/Spinner';
import './styles.css';

export const SensorMonitoring = () => {
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [devicesData, setDevicesData] = useState([] as IDevice[]);
  const [hasError, setHasError] = useState(false);
  const intervalDevicesFetchId = useRef(0);

  const fetchDevices = async () => {
    try {
      const response: IDevice[] = await apiClient.get(ENDPOINTS.devices);
      setHasError(false);
      setDevicesData(response);
      logger.log('Devices', { response });
    } catch (error) {
      logger.log('error fetching devices:', error);
      setHasError(true);
    }
  };

  const fetchDevicesWithLoading = async () => {
    setIsLoading(true);
    await fetchDevices();
    setIsLoading(false);
  };

  useEffect(() => {
    if (isFirstLoad && !isLoading) {
      fetchDevicesWithLoading();
    }
  }, []);

  useEffect(() => {
    if (isFirstLoad) return;

    intervalDevicesFetchId.current = window.setInterval(fetchDevices, APP_CONFIG.intervals.devices);

    return () => clearInterval(intervalDevicesFetchId.current);
  }, [isFirstLoad]);

  useEffect(() => {
    setIsFirstLoad(hasError);

    if (hasError) {
      clearInterval(intervalDevicesFetchId.current);
    }
  }, [hasError]);

  if (hasError) {
    return (
      <div className="full-height-with-header flex-abs-center">
        Error loading devices information,{' '}
        <div role="button" className="device-wrapper-link" onClick={fetchDevicesWithLoading}>
          try again
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="full-height-with-header flex-abs-center device-wrapper-spinner">
        <Spinner />
        Loading devices...
      </div>
    );
  }

  if (devicesData.length === 0) {
    return <div className="full-height-with-header flex-abs-center">No devices detected</div>;
  }

  return (
    <div className="device-wrapper">
      {devicesData.map((deviceInfo) => (
        <Device data={deviceInfo} key={deviceInfo.wireless_device_id} />
      ))}
    </div>
  );
};
