// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { UseQueryOptions, useQueries } from 'react-query';
import { apiClient } from '../../../../apiClient';
import { ENDPOINTS } from '../../../../endpoints';
import { IWirelessDeviceStatus } from '../../../../types';
import { AxiosError } from 'axios';
import { APP_CONFIG } from '../../../../appConfig';
import { Collapse, Spin } from 'antd';
import toast from 'react-hot-toast';
import { CaretRightOutlined } from '@ant-design/icons';
import { useRowScroller } from '../ScrollManager';
import { TransferStatus } from '../../../../components/TransferStatus/TransferStatus';
import { useEffect, useRef } from 'react';
import { logger } from '../../../../utils/logger';

interface Props {
  devices: Array<string>;
  taskId: string;
}

export const DevicesStatutes = ({ devices, taskId }: Props) => {
  const scrollManager = useRowScroller();
  const progressCellElement = useRef<HTMLElement>();

  const results = useQueries(
    devices.map(
      (deviceId): UseQueryOptions<IWirelessDeviceStatus, AxiosError> => ({
        queryKey: ['deviceById', deviceId],
        queryFn: () => apiClient.get(`${ENDPOINTS.getDevicesByTaskId}?fuotaTaskId=${deviceId}`),
        refetchOnWindowFocus: false,
        retry: false,
        refetchInterval: (data) => {
          if (data?.status === 'PENDING' || data?.status === 'TRANSFERRING') {
            return APP_CONFIG.intervals.otaProgressTasks;
          }

          return false;
        },
        onError: (error) => {
          logger.log('error fetching', error);
          toast.error('Error while getting device status');
        }
      })
    )
  );

  const isError = results.some((result) => result.isError);
  const isLoading = results.some((result) => result.isLoading);

  useEffect(() => {
    progressCellElement.current = document.querySelector(`[data-row-key="${taskId}"] > .progress-task-id`) as HTMLElement;
  }, []);

  // progress column logic
  useEffect(() => {
    if (!progressCellElement.current) return;

    const count = results.reduce((acc: number, item) => {
      if (item.data?.status !== 'PENDING' && item.data?.status !== 'TRANSFERRING') {
        acc += 1;
      }

      return acc;
    }, 0);

    // we are manipulating the DOM directly for better efficiency
    progressCellElement.current.innerHTML = `${count}/${results.length}`;
  }, [results]);

  if (isError) {
    return <>-</>;
  }

  if (isLoading) {
    return (
      <span className="flex-abs-center" style={{ justifyContent: 'space-around' }}>
        Loading statuses <Spin size="small" />
      </span>
    );
  }

  const Label = () => (
    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap', maxWidth: '200px', justifyContent: 'space-between' }}>
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
          • {status}: {count}
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
