// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import classNames from "classnames";
import { useEffect, useState } from "react";
import { ReactComponent as PowerButton } from "../../../assets/icons/power-off-solid.svg";
import "./styles.css";

interface Props {
  serialNumber?: number;
  initialState: boolean;
}

export const EngageButton = ({ serialNumber, initialState }: Props) => {
  const [isPowerButtonOn, setIsPowerButtonOn] = useState(false);

  useEffect(() => {
    setIsPowerButtonOn(initialState);
  }, [initialState]);

  return (
    <div className="engage-button-section">
      <button
        className={classNames(
          "stats-power-button",
          "flex-abs-center",
          isPowerButtonOn && "on"
        )}
      >
        <span
          className={classNames(
            "no-selection",
            "mr-2",
            isPowerButtonOn ? "green" : "black"
          )}
        >
          {serialNumber}
        </span>
        <div className="flex-abs-center">
          <PowerButton
            width={25}
            height={25}
            fill={isPowerButtonOn ? "green" : "black"}
          />
          <span
            className={classNames(
              "no-selection",
              "engaged-text",
              isPowerButtonOn ? "green" : "black"
            )}
          >
            {isPowerButtonOn ? "Engaged" : "Disengaged"}
          </span>
        </div>
      </button>
    </div>
  );
};
