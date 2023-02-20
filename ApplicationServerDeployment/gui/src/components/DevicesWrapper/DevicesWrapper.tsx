// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useEffect, useRef, useState } from "react";
import { apiClient } from "../../apiClient";
import { APP_CONFIG } from "../../appConfig";
import { ENDPOINTS } from "../../endpoints";
import { IDevice } from "../../types";
import { verifyAuth } from "../../utils";
import { logger } from "../../utils/logger";
import { Device } from "../Device/Device";
import { Spinner } from "../Spinner/Spinner";
import "./styles.css";

export const DevicesWrapper = () => {
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [devicesData, setDevicesData] = useState([] as IDevice[]);
  const [hasError, setHasError] = useState(false);
  const intervalDevicesFetchId = useRef(0);

  const fetchDevices = async () => {
    try {
      const response = await apiClient.get<IDevice[]>(ENDPOINTS.devices);

      verifyAuth(response.status);

      setDevicesData(response.data);
      logger.log("Devices", { response: response.data });
    } catch (error) {
      logger.log("error fetching devices:", error);
      setHasError(true);
    }
  };

  const fetchDevicesWithLoading = async () => {
    setHasError(false);
    setIsLoading(true);
    await fetchDevices();
    setIsLoading(false);
    setIsFirstLoad(false);
  };

  useEffect(() => {
    if (isFirstLoad && !isLoading) {
      fetchDevicesWithLoading();
    }
  }, []);

  useEffect(() => {
    if (isFirstLoad) return;

    intervalDevicesFetchId.current = window.setInterval(
      fetchDevices,
      APP_CONFIG.intervals.devices
    );

    return () => clearInterval(intervalDevicesFetchId.current);
  }, [isFirstLoad]);

  useEffect(() => {
    if (!hasError) return;
    clearInterval(intervalDevicesFetchId.current);
  }, [hasError]);

  if (hasError) {
    return (
      <div className="full-height-with-header flex-abs-center">
        Error loading devices information,{" "}
        <div
          role="button"
          className="device-wrapper-link"
          onClick={fetchDevicesWithLoading}
        >
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
    return (
      <div className="full-height-with-header flex-abs-center">
        No devices detected
      </div>
    );
  }

  return (
    <div className="device-wrapper">
      {devicesData.map((deviceInfo) => (
        <Device data={deviceInfo} key={deviceInfo.wireless_device_id} />
      ))}
    </div>
  );
};
