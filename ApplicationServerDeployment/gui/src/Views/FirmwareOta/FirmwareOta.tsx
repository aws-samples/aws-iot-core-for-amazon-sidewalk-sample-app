import classNames from 'classnames';
import { Instructions } from './Components/Instructions';
import { TranserTasksTable } from './Components/TransferTasksTable';
import { WirelessDevicesTable } from './Components/WirelessDevicesTable';
import styles from './styles.module.css';

export const FirmwareOta = () => {
  return (
    <div className={classNames('p-3', styles.container)}>
      <Instructions />
      <WirelessDevicesTable />
      <TranserTasksTable />
    </div>
  );
};
