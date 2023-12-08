import { UseQueryOptions, useQueries } from 'react-query';
import { apiClient } from '../../../../apiClient';
import { ENDPOINTS } from '../../../../endpoints';
import { IWirelessDeviceStatus } from '../../../../types';
import { AxiosError } from 'axios';
import { APP_CONFIG } from '../../../../appConfig';
import { Collapse, Spin } from 'antd';
import toast from 'react-hot-toast';
import { verifyAuth } from '../../../../utils';
import { CaretRightOutlined } from '@ant-design/icons';
import { useRowScroller } from '../ScrollManager';
import { TransferStatus } from '../../../../components/TransferStatus/TransferStatus';

interface Props {
  devices: Array<string>;
}

export const DevicesStatutes = ({ devices }: Props) => {
  const scrollManager = useRowScroller();

  const results = useQueries(
    devices.map(
      (deviceId): UseQueryOptions<IWirelessDeviceStatus, AxiosError> => ({
        queryKey: ['deviceById', deviceId],
        queryFn: () => apiClient.get(`${ENDPOINTS.getDevicesByTaskId}?fuotaTaskId=${deviceId}`).then((res) => res.data),
        refetchOnWindowFocus: false,
        retry: false,
        refetchInterval: (data) => {
          if (data?.status === 'PENDING' || data?.status === 'TRANSFERRING') {
            return APP_CONFIG.intervals.otaProgressTasks;
          }

          return false;
        },
        onError: (error) => {
          verifyAuth(error.response?.status!);
          toast.error('Error while getting device status');
        }
      })
    )
  );

  const isError = results.some((result) => result.isError);
  const isLoading = results.some((result) => result.isLoading);

  if (isError) {
    return <>Devices</>;
  }

  if (isLoading) {
    return (
      <span className="flex-abs-center" style={{ justifyContent: 'space-around' }}>
        Loading statuses <Spin size="small" />
      </span>
    );
  }

  const Label = () => (
    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap', maxWidth: '200px' }}>
      {Object.entries(
        results.reduce<{ [key: string]: number }>((acc, { data }) => {
          if (data?.status! in acc) {
            acc[data?.status!] += 1;
          } else {
            acc[data?.status!] = 1;
          }

          return acc;
        }, {})
      ).map(([status, count], index, arr) => (
        <span key={`${index}${status}`}>
          {status}: {count} {arr.length !== index + 1 && '|'}
        </span>
      ))}
    </div>
  );

  return (
    <Collapse
      bordered={false}
      expandIcon={({ isActive }) => <CaretRightOutlined rotate={isActive ? 90 : 0} />}
      style={{ background: 'light-gray' }}
      items={[
        {
          key: '1',
          label: <Label />,
          children: (
            <ul style={{ margin: 0 }}>
              {results.map(({ data }) => (
                <li key={data?.device_id} style={{ display: 'flex', gap: '5px' }}>
                  <a onClick={() => scrollManager.scrollTo(data?.device_id!, 'devices')}>{data?.device_id}</a>
                  : <TransferStatus type={data?.status!} />
                </li>
              ))}
            </ul>
          ),
          style: {
            padding: 0
          }
        }
      ]}
    />
  );
};
