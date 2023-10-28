// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Link } from "react-router-dom";
import amazonLogo from "../../assets/images/amazon-sidewalk-logo.png";
import { useAuth } from "../../hooks/useAuth";
import "./styles.css";
import { Routes } from "../../routes";

export const Header = () => {
  const { isAuthorized } = useAuth();
  return (
    <header>
      <h2>Sensor Monitoring App</h2>
      <div className="container-menu">
        {isAuthorized && (
          <div className="menu">
            <Link to={Routes.sensorMonitoring}>Sensor Monitoring</Link>
            <span> | </span>
            <Link to={Routes.firmwareOTA}>Firmware OTA</Link>
          </div>
        )}
        <img src={amazonLogo} className="header-img" />
      </div>
    </header>
  );
};
