// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import classNames from "classnames";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { apiClient } from "../../../apiClient";
import { ReactComponent as ToogleOff } from "../../../assets/icons/toggle-large-off-solid.svg";
import { ReactComponent as ToogleOn } from "../../../assets/icons/toggle-large-on-regular.svg";
import { LED_STATE } from "../../../constants";
import { ENDPOINTS, interpolateParams } from "../../../endpoints";
import { IDevice } from "../../../types";
import { logger } from "../../../utils/logger";
import "./styles.css";

interface Props {
  serialNumber?: number;
  ledId: number;
  deviceId: string;
  initialState: boolean;
}

export const LedButton = ({
  serialNumber,
  initialState,
  ledId,
  deviceId,
}: Props) => {
  const [isToogleOn, setIsToggleOn] = useState(false);
  const [isNotifying, setIsNotifying] = useState(false);
  const [hasNotificationFailed, setHasNotificationFailed] = useState(false);

  const hasLedStateBeenSetInDb = async (
    deviceId: string,
    ledId: number,
    nextState: string
  ) => {
    let hasValueBeenSet = false;
    let hasTimeouted = false;
    const TIME = 5000;

    // Race condition between timeout and check value in db
    const timeoutId = setTimeout(() => {
      hasTimeouted = true;
    }, TIME);

    while (hasValueBeenSet === false && hasTimeouted === false) {
      const deviceStateFromDb = await apiClient.get<IDevice>(
        interpolateParams(ENDPOINTS.device, { id: deviceId })
      );

      hasValueBeenSet =
        nextState === LED_STATE.ON
          ? deviceStateFromDb.data.led_on.includes(ledId)
          : !deviceStateFromDb.data.led_on.includes(ledId);
    }

    clearTimeout(timeoutId);

    return hasValueBeenSet;
  };

  const notifyLedToogle = async () => {
    setIsNotifying(true);
    const nextLedState = isToogleOn ? LED_STATE.OFF : LED_STATE.ON;

    try {
      await apiClient.post(ENDPOINTS.led, {
        command: "DEMO_APP_ACTION_REQ",
        deviceId,
        ledId,
        action: nextLedState,
      });

      const shouldToggleLed = await hasLedStateBeenSetInDb(
        deviceId,
        ledId,
        nextLedState
      );

      if (shouldToggleLed) {
        setIsToggleOn((prevValue) => !prevValue);
      }
    } catch (error) {
      setHasNotificationFailed(true);
      logger.log("error notifying led", error);
      toast("Error notifying led, try again later");
    } finally {
      setIsNotifying(false);
    }
  };

  useEffect(() => {
    if (isNotifying) return;
    setIsToggleOn(initialState);
  }, [initialState]);

  return (
    <div className="flex-abs-center led-section">
      {isToogleOn ? (
        <span className={classNames("led-section-indicator-on")}>On</span>
      ) : (
        <span className={classNames("led-section-indicator-off")}>Off</span>
      )}
      <button
        className="flex-abs-center led-section-toggle-button"
        onClick={notifyLedToogle}
        disabled={isNotifying}
      >
        {isToogleOn ? (
          <>
            <ToogleOn fill="green" width={25} height={25} />
          </>
        ) : (
          <>
            <ToogleOff width={25} height={25} />
          </>
        )}
      </button>
      <span className="mt-1 no-selection">LED {serialNumber}</span>
    </div>
  );
};
