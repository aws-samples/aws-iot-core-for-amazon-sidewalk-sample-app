// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { NavLink } from 'react-router-dom';
import amazonLogo from '../../assets/images/amazon-sidewalk-logo.png';
import { useAuth } from '../../hooks/useAuth';
import styles from './styles.module.css';
import { Routes } from '../../routes';

export const Header = () => {
  const { isAuthorized } = useAuth();

  const setActiveLink = ({ isActive }: { isActive: boolean }) => (isActive ? styles.activeLink : undefined);

  return (
    <header>
      <h2>Sidewalk Sample App</h2>
      <div className={styles.containerMenu}>
        {isAuthorized && (
          <div className={styles.menu}>
            <NavLink className={setActiveLink} to={Routes.sensorMonitoring}>
              Sensor Monitoring
            </NavLink>
            <span> | </span>
            <NavLink className={setActiveLink} to={Routes.firmwareOTA}>
              Firmware OTA
            </NavLink>
          </div>
        )}
        <img src={amazonLogo} className={styles.headerImage} />
      </div>
    </header>
  );
};
