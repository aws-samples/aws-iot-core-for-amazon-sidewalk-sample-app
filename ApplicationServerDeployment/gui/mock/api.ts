import wirelessDevicesData from './wirelessDevices.json';
import transferTasks from './transferTasks.json';
import startTransferTasks from './startTransferTasks.json';
import s3FileNames from './s3Filenames.json';
import progressMock1_device1 from './progressMocks/device1/wirelessDevices1.json';
import progressMock2_device1 from './progressMocks/device1/wirelessDevices2.json';
import progressMock3_device1 from './progressMocks/device1/wirelessDevices3.json';
import progressMock4_device1 from './progressMocks/device1/wirelessDevices4.json';
import progressMock5_device1 from './progressMocks/device1/wirelessDevices5.json';
import progressMock6_device1 from './progressMocks/device1/wirelessDevices6.json';
import progressMock1_device2 from './progressMocks/device2/wirelessDevices1.json';
import progressMock2_device2 from './progressMocks/device2/wirelessDevices2.json';
import progressMock3_device2 from './progressMocks/device2/wirelessDevices3.json';
import progressMock4_device2 from './progressMocks/device2/wirelessDevices4.json';
import progressMock5_device2 from './progressMocks/device2/wirelessDevices5.json';

const devicesMocks = {
  ['6540562b20d2ed23212f08ad']: [
    progressMock1_device1,
    progressMock2_device1,
    progressMock3_device1,
    progressMock4_device1,
    progressMock5_device1,
    progressMock6_device1
  ],
  ['6540562b9a43699094046e4c']: [
    progressMock1_device2,
    progressMock2_device2,
    progressMock3_device2,
    progressMock4_device2,
    progressMock5_device2
  ]
};

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
    method: 'post',
    response: () => undefined
  },
  {
    url: '/api/otaGetS3',
    method: 'get',
    response: () => s3FileNames,
    statusCode: 200
  },
  {
    url: '/api/otaUpload',
    method: 'post',
    response: () => undefined,
    statusCode: 200
  },
  {
    url: '/api/ota/deviceTransfers/:id',
    method: 'get',
    response: ({ query }) => {
      const [deviceId, mockToGet] = query.id.split('_');
      const mockDeviceMap = devicesMocks[deviceId];

      switch (Number(mockToGet)) {
        case 1:
          return mockDeviceMap[0];
          break;

        case 2:
          return mockDeviceMap[1];

          break;

        case 3:
          return mockDeviceMap[2];

          break;

        case 4:
          return mockDeviceMap[3];

          break;

        case 5:
          return mockDeviceMap[4];

          break;

        case 6:
          return mockDeviceMap[5];

          break;

        default:
          return mockDeviceMap[0];
          break;
      }
    },
    statusCode: 200
  },
  {
    url: '/api/otaSetCurrentFirmware',
    method: 'post',
    response: () => undefined,
    timeout: 3000,
    statusCode: 200
  }
];
