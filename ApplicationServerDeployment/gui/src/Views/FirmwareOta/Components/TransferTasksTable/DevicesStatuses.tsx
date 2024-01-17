// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { UseQueryOptions } from 'react-query';
import { apiClient } from '../../../../apiClient';
import { ENDPOINTS, interpolateParams } from '../../../../endpoints';
import { IWirelessDevice, IWirelessDeviceStatus } from '../../../../types';
import { AxiosError } from 'axios';
import { APP_CONFIG } from '../../../../appConfig';
import { Collapse, Spin } from 'antd';
import toast from 'react-hot-toast';
import { CaretRightOutlined } from '@ant-design/icons';
import { useRowScroller } from '../ScrollManager';
import { TransferStatus } from '../../../../components/TransferStatus/TransferStatus';
import { useEffect, useRef } from 'react';
import { logger } from '../../../../utils/logger';
import { useQueriesWithRefetch } from '../../../../utils';
import { queryClient } from '../../../../App';
import { MOCK_MODE } from '../../../../constants';

interface Props {
  devices: Array<string>;
  taskId: string;
  forceRefetching: boolean;
}

export const DevicesStatutes = ({ devices, taskId, forceRefetching }: Props) => {
  const scrollManager = useRowScroller();
  const progressCellElement = useRef<HTMLElement>();

  let { results, refetchAll } = useQueriesWithRefetch(
    devices.map(
      (deviceId): UseQueryOptions<IWirelessDevice, AxiosError> => ({
        queryKey: ['deviceById', deviceId],
        queryFn: () =>
          apiClient.get(interpolateParams(ENDPOINTS.getDeviceById, { id: deviceId }).concat(MOCK_MODE ? '/mock' : '')),
        refetchOnWindowFocus: false,
        cacheTime: 0,
        retry: false,
        refetchInterval: (data) => {
          if (data?.transferStatus === 'PENDING' || data?.transferStatus === 'TRANSFERRING') {
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

  const isError = results.some((result) => result.isError || result.isRefetchError);
  const isLoading = results.some((result) => result.isLoading);

  useEffect(() => {
    progressCellElement.current = document.querySelector(`[data-row-key="${taskId}"] > .progress-task-id`) as HTMLElement;
  }, []);

  // progress column logic
  useEffect(() => {
    if (!progressCellElement.current || isLoading) return;

    const count = results.reduce((acc: number, item) => {
      if (item.data?.transferStatus !== 'PENDING' && item.data?.transferStatus !== 'TRANSFERRING') {
        acc += 1;
      }

      return acc;
    }, 0);

    // we are manipulating the DOM directly for better efficiency
    progressCellElement.current.innerHTML = `${count}/${results.length}`;

    () => {
      if (progressCellElement.current) {
        progressCellElement.current.innerHTML = '';
      }
    };
  }, [results, isLoading]);

  useEffect(() => {
    if (!forceRefetching) return;

    if (progressCellElement.current) {
      progressCellElement.current.innerHTML = '';
    }

    const promises = devices.map((deviceId) => queryClient.resetQueries({ queryKey: ['deviceById', deviceId] }));

    Promise.all(promises).then(() => {
      refetchAll();
    });
  }, [forceRefetching]);

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
          if (data?.transferStatus! in acc) {
            acc[data?.transferStatus!] += 1;
          } else {
            acc[data?.transferStatus!] = 1;
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
                <li key={data?.deviceId} style={{ display: 'flex', gap: '5px' }}>
                  {scrollManager.checkReferenceExistance(data?.deviceId!, 'devices') ? (
                    <a onClick={() => scrollManager.scrollTo(data?.deviceId!, 'devices')}>{data?.deviceId}</a>
                  ) : (
                    <>{data?.deviceId}</>
                  )}
                  : <TransferStatus type={data?.transferStatus!} />
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
