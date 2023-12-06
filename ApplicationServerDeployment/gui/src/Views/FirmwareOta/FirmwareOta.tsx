import classNames from 'classnames';
import { Instructions } from './components/Instructions';
import { TranserTasksTable } from './components/TransferTasksTable/Table';
import { WirelessDevicesTable } from './components/WirelessDevicesTable/Table';
import styles from './styles.module.css';
import { ScrollProvider } from './components/ScrollManager';

export const FirmwareOta = () => {
  return (
    <div className={classNames('p-3', styles.container)}>
      <Instructions />
      <ScrollProvider>
        <WirelessDevicesTable />
        <TranserTasksTable />
      </ScrollProvider>
    </div>
  );
};
