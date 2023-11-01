import wirelessDevicesData from './wirelessDevices.json';
import transferTasks from './transferTasks.json';

export default [
  {
    url: "/api/wireless-devices",
    method: "get",
    response: ({ query }) => wirelessDevicesData
  },
  {
    url: "/api/transfer-tasks",
    method: "get",
    response: ({ query }) => transferTasks
  },
];
