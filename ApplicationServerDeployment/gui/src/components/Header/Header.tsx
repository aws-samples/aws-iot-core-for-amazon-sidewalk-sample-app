// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import amazonLogo from '../../assets/images/amazon-sidewalk-logo.png';
import './styles.css';

export const Header = () => (
  <header>
    <h2>Sensor Monitoring App</h2>
    <img src={amazonLogo} className="header-img" />
  </header>
);
