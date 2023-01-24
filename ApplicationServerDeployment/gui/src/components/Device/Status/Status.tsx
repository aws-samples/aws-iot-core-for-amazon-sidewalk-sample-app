// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { ReactComponent as CombinedCloudCircuitIcon } from "../../../assets/icons/Combined-cloud-circuit.svg";
import { ReactComponent as CirculeSolidIcon } from "../../../assets/icons/circle-solid.svg";
import { ReactComponent as EyeRegularIcon } from "../../../assets/icons/eye-regular.svg";
import { ReactComponent as SignalIcon } from "../../../assets/icons/signal-stream-solid.svg";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en.json";
import ReactTimeAgo from "react-time-ago";
import "./styles.css";
import { useEffect, useState } from "react";

TimeAgo.addDefaultLocale(en);

interface Props {
  name: string;
  lastUplink: number;
  isOffline: boolean;
  linkType: string;
}

export const Status = ({ name, lastUplink, isOffline, linkType }: Props) => {
  return (
    <div className="status-section">
      <div className="status-section-icon-wrapper">
        <CombinedCloudCircuitIcon width={75} height={60} />
      </div>
      <div className="status-section-right-column-wrapper">
        <h2 className="title-h2">{name}</h2>
        <div className="status-section-device-info">
          <div className="flex-abs-center status-section-status">
            <CirculeSolidIcon
              width={10}
              height={18}
              fill={isOffline ? "black" : "green"}
            />
            <span className="status-section-info-text">
              {isOffline ? "Offline" : "Online"}
            </span>
          </div>
          <div className="flex-abs-center status-section-last-beat">
            <EyeRegularIcon width={15} height={18} />
            <span className="status-section-info-text">
              <ReactTimeAgo
                date={lastUplink}
                locale="en-US"
                timeStyle="twitter"
              />{" "}
              ago
            </span>
          </div>
          {!isOffline && (
            <div className="flex-abs-center status-section-signal">
              <SignalIcon width={15} height={18} />
              <span className="status-section-info-text">{linkType}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
