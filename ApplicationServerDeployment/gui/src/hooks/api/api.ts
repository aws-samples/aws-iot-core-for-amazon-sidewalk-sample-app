// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { useMutation, useQuery, UseMutationOptions } from 'react-query';
import { apiClient } from '../../apiClient';
import { ENDPOINTS } from '../../endpoints';
import {
  ICancelTask,
  IS3Files,
  ISetCurrentFirmware,
  IStartTransferTask,
  ITransferTasks,
  IWirelessDevices
} from '../../types';
import { RcFile } from 'antd/es/upload/interface';
import toast from 'react-hot-toast';
import { convertToBase64 } from '../../utils';
import { AxiosError } from 'axios';
import { logger } from '../../utils/logger';

type ConfigMutation = Omit<UseMutationOptions<{}, AxiosError, {}, {}>, 'mutationKey' | 'mutationFn'>;

export const useGetWirelessDevices = () =>
  useQuery<IWirelessDevices, AxiosError>(['getWirelessDevices'], () => apiClient.get(ENDPOINTS.otaDevices), {
    cacheTime: 0,
    onError: (error) => {
      logger.log('error fetching', error);
      toast.error('Error fetching Wireless Devices');
    }
  });

export const useGetTransferTasks = () =>
  useQuery<ITransferTasks, AxiosError>(['getTransferTasks'], () => apiClient.get(ENDPOINTS.otaTasks), {
    cacheTime: 0,
    onError: (error) => {
      logger.log('error fetching', error);
      toast.error('Error fetching Transfer Tasks');
    }
  });

export const useS3Upload = (config?: ConfigMutation) =>
  useMutation(
    ['upload'],
    async (payload: RcFile) => {
      const base64 = await convertToBase64(payload);
      return apiClient.post(ENDPOINTS.upload, {
        filename: payload.name,
        file: base64
      });
    },
    {
      retry: false,
      onError: (error: AxiosError) => {
        logger.log('error fetching', error);
        toast.error('Error while trying to upload a file');
      },
      onSuccess: () => {
        toast.success('File Uploaded');
      },
      ...config
    }
  );

export const useGetFileNames = () =>
  useQuery<IS3Files, AxiosError>(['getFilenames'], () => apiClient.get(ENDPOINTS.s3Filenames), {
    retry: false,
    onError: (error) => {
      logger.log('error fetching', error);
      toast.error('Error getting filenames');
    }
  });

export const useStartTransferTask = (config?: ConfigMutation) =>
  useMutation(
    ['startTrasnferTask'],
    (payload: IStartTransferTask) => apiClient.post(ENDPOINTS.startTransferTasks, payload),
    {
      onError: (error: AxiosError) => {
        logger.log('error posting', error);
        toast.error('Error while trying to start a transfer task');
      },
      ...config
    }
  );

export const useCancelTask = (config?: ConfigMutation) =>
  useMutation(['cancelTask'], (payload: ICancelTask) => apiClient.post(ENDPOINTS.cancelTransferTasks, payload), {
    onError: (error: AxiosError) => {
      logger.log('error posting', error);
      toast.error('Error while trying to cancel a transfer task');
    },
    ...config
  });

export const useSetCurrentFirmware = (config?: ConfigMutation) =>
  useMutation(
    ['setCurrentFirmware'],
    (payload: ISetCurrentFirmware) => apiClient.post(ENDPOINTS.setCurrentFirmware, payload),
    {
      onError: (error: AxiosError) => {
        logger.log('error posting', error);
        toast.error('Error while trying to set current firmware');
      },
      ...config
    }
  );
