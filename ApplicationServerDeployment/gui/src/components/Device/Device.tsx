// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import classNames from "classnames";
import { TemperatureChart } from "./TemperatureChart/TemperatureChart";
import { LedButton } from "./LedButton/LedButton";
import "./styles.css";
import { Status } from "./Status/Status";
import { EngageButton } from "./EngageButton/EngageButton";
import { IDevice } from "../../types";
import { useEffect, useState } from "react";
import { APP_CONFIG } from "../../appConfig";

interface Props {
  data: IDevice;
}

export const Device = ({ data }: Props) => {
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    const intervalId = setInterval(() => {
      const TTL = 60 * 1000;
      const diff = Date.now() - data.last_uplink * 1000;
      const hasTimeToLivePassed = diff > TTL;
      setIsOffline(hasTimeToLivePassed);
    }, APP_CONFIG.intervals.online);

    return () => clearInterval(intervalId);
  }, [data.last_uplink]);

  const hasNoCapabilities =
    data.led.length === 0 && data.button.length === 0 && !data.sensor;

  if (hasNoCapabilities) {
    return (
      <div className="full-height-with-header container-offline">
        <section className="title">
          <Status
            name={data.wireless_device_id}
            lastUplink={data.last_uplink * 1000}
            linkType={data.link_type}
            isOffline={isOffline}
          />
        </section>
        <section className="offline offline-text flex-abs-center">
          <p>
            No device capabilities info. <br />
            Please restart your device.
          </p>
        </section>
      </div>
    );
  }

  return (
    <div className="container">
      <section className="title">
        <Status
          name={data.wireless_device_id}
          lastUplink={data.last_uplink * 1000}
          linkType={data.link_type}
          isOffline={isOffline}
        />
      </section>

      <>
        <section className="led">
          {data.led.length > 0 && (
            <div className="led-wrapper">
              {data.led.map((ledId) => {
                const hasOneLedOnly = data.led.length === 1;
                const isToggleOn = data.led_on.includes(ledId);

                return (
                  <LedButton
                    initialState={isToggleOn}
                    serialNumber={hasOneLedOnly ? undefined : ledId + 1}
                    deviceId={data.wireless_device_id}
                    ledId={ledId}
                    key={ledId}
                    isOffline={isOffline}
                  />
                );
              })}
            </div>
          )}
        </section>
        <section className="chart">
          <TemperatureChart
            deviceId={data.wireless_device_id}
            sensorUnit={data.sensor_unit}
            isSensorOn={data.sensor}
          />
        </section>
        <section className="ebuttons">
          {data.button.length > 0 && (
            <>
              <div className="ebuttons-section-title flex-abs-center">
                Push button on device
              </div>
              <div className="ebuttons-wrapper">
                {data.button.map((buttonId) => {
                  const hasOneButtonOnly = data.button.length === 1;
                  const isButtonOn = data.button_pressed.includes(buttonId);

                  return (
                    <EngageButton
                      initialState={isButtonOn}
                      serialNumber={hasOneButtonOnly ? undefined : buttonId + 1}
                      key={buttonId}
                    />
                  );
                })}
              </div>
            </>
          )}
        </section>
      </>
    </div>
  );
};
