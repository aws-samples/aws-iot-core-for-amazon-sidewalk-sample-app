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
      const hasTimeToLivePassed = Date.now() > data.time_to_live * 1000;
      setIsOffline(hasTimeToLivePassed);
    }, APP_CONFIG.intervals.online);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className={classNames(isOffline ? "container-offline" : "container")}>
      <section className="title">
        <Status
          name={data.wireless_device_id}
          lastUplink={data.last_uplink * 1000}
          linkType={data.link_type}
          isOffline={isOffline}
        />
      </section>

      {!isOffline ? (
        <>
          <section className="led">
            <div className="led-wrapper">
              {data.led.map((ledId, index) => {
                const hasOneLedOnly = data.led.length === 1;
                const isToggleOn = data.led_on.includes(ledId);

                return (
                  <LedButton
                    initialState={isToggleOn}
                    serialNumber={hasOneLedOnly ? undefined : ledId + 1}
                    deviceId={data.wireless_device_id}
                    ledId={ledId}
                    key={ledId}
                  />
                );
              })}
            </div>
          </section>
          <section className="chart">
            <TemperatureChart
              deviceId={data.wireless_device_id}
              sensorUnit={data.sensor_unit}
              isSensorOn={data.sensor}
            />
          </section>
          <section className="ebuttons">
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
          </section>
        </>
      ) : (
        <section className="offline">
          <div className="flex-abs-center offline-text">
            Device Offline. <br />
            Device information unavailable.
          </div>
        </section>
      )}
    </div>
  );
};
