import { Instructions } from './Components/Instructions';
import { TranserTasksTable } from './Components/TransferTasksTable';
import { WirelessDevicesTable } from './Components/WirelessDevicesTable';

export const FirmwareOta = () => {
  return (
    <div className="p-3">
      <Instructions />
      <WirelessDevicesTable />
      <TranserTasksTable />
    </div>
  );
};
