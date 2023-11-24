import wirelessDevicesData from './wirelessDevices.json';
import transferTasks from './transferTasks.json';
import startTransferTasks from './startTransferTasks.json';
import s3FileNames from './s3Filenames.json';

export default [
  {
    url: '/api/ota/deviceTransfers',
    method: 'get',
    response: ({ query }) => wirelessDevicesData
  },
  {
    url: '/api/ota/transferTasks',
    method: 'get',
    response: ({ query }) => transferTasks
  },
  {
    url: '/api/otaStart',
    method: 'post',
    response: () => startTransferTasks,
    timeout: 3000
  },
  {
    url: '/api/otaCancel',
    method: 'delete',
    response: () => undefined
  },
  {
    url: '/api/otaGetS3',
    method: 'post',
    response: () => s3FileNames,
    statusCode: 200
  },
  {
    url: '/api/otaUpload',
    method: 'post',
    response: () => undefined,
    statusCode: 200
  }
];
