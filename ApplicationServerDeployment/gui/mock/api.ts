import wirelessDevicesData from './wirelessDevices.json';
import transferTasks from './transferTasks.json';
import startTransferTasks from './startTransferTasks.json';
import s3FileNames from './s3Filenames.json';

export default [
  {
    url: '/api/wireless-devices',
    method: 'get',
    response: ({ query }) => wirelessDevicesData
  },
  {
    url: '/api/transfer-tasks',
    method: 'get',
    response: ({ query }) => transferTasks
  },
  {
    url: '/api/start-transfer-tasks',
    method: 'post',
    response: () => startTransferTasks,
    timeout: 3000
  },
  {
    url: '/api/cancel-transfer-tasks',
    method: 'delete',
    response: () => undefined
  },
  {
    url: '/api/filenames',
    method: 'get',
    response: () => s3FileNames
  },
  {
    url: '/api/upload',
    method: 'post',
    response: () => undefined,
    statusCode: 200
  }
];
