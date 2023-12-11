// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import classNames from 'classnames';
import { Instructions } from './components/Instructions';
import { TranserTasksTable } from './components/TransferTasksTable/Table';
import { WirelessDevicesTable } from './components/WirelessDevicesTable/Table';
import { ScrollProvider } from './components/ScrollManager';
import { FirmwareConfig } from './components/FirmwareConfig';
import styles from './styles.module.css';

export const FirmwareOta = () => {
  return (
    <div className={classNames('p-3', styles.container)}>
      <div className={classNames(styles.containerFlex)}>
        <Instructions />
        <FirmwareConfig />
      </div>
      <ScrollProvider>
        <WirelessDevicesTable />
        <TranserTasksTable />
      </ScrollProvider>
    </div>
  );
};
