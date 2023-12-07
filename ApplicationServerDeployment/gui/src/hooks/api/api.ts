import { useMutation, useQuery, UseMutationOptions, QueryFunctionContext, QueryFunction } from 'react-query';
import { apiClient } from '../../apiClient';
import { ENDPOINTS } from '../../endpoints';
import {
  ICancelTask,
  IS3Files,
  ISetCurrentFirmware,
  IStartTransferTask,
  ITransferTasks,
  IWirelessDevice,
  IWirelessDevices
} from '../../types';
import { RcFile } from 'antd/es/upload/interface';
import toast from 'react-hot-toast';
import { convertToBase64, verifyAuth } from '../../utils';
import { AxiosError } from 'axios';

type ConfigMutation = Omit<UseMutationOptions<{}, AxiosError, {}, {}>, 'mutationKey' | 'mutationFn'>;

export const useGetWirelessDevices = () =>
  useQuery<IWirelessDevices, AxiosError>(
    ['getWirelessDevices'],
    () => apiClient.get(ENDPOINTS.otaDevices).then((res) => res.data),
    {
      refetchOnWindowFocus: false,
      onError: (error) => {
        console.log('error fetching', error);
        verifyAuth(error.status!);
        toast.error('Error fetching Wireless Devices');
      }
    }
  );

export const useGetTransferTasks = () =>
  useQuery<ITransferTasks, AxiosError>(
    ['getTransferTasks'],
    () => apiClient.get(ENDPOINTS.otaTasks).then((res) => res.data),
    {
      cacheTime: Infinity,
      refetchOnWindowFocus: false,
      onError: (error) => {
        verifyAuth(error.status!);
        toast.error('Error fetching Transfer Tasks');
      }
    }
  );

export const useS3Upload = (config?: ConfigMutation) =>
  useMutation(
    ['upload'],
    async (payload: RcFile) => {
      const base64 = await convertToBase64(payload);
      return apiClient
        .post(ENDPOINTS.upload, {
          filename: payload.name,
          file: base64
        })
        .then((res) => res.data);
    },
    {
      retry: false,
      onError: (error: AxiosError) => {
        verifyAuth(error.status!);
        toast.error('Error while trying to upload a file');
      },
      onSuccess: () => {
        toast.success('File Uploaded');
      },
      ...config
    }
  );

export const useGetFileNames = () =>
  useQuery<IS3Files, AxiosError>(['getFilenames'], () => apiClient.get(ENDPOINTS.s3Filenames).then((res) => res.data), {
    retry: false,
    refetchOnWindowFocus: false,
    onError: (error) => {
      verifyAuth(error.status!);
      toast.error('Error getting filenames');
    }
  });

export const useStartTransferTask = (config?: ConfigMutation) =>
  useMutation(
    ['startTrasnferTask'],
    (payload: IStartTransferTask) => apiClient.post(ENDPOINTS.startTransferTasks, payload).then((res) => res.data),
    {
      onError: (error: AxiosError) => {
        verifyAuth(error.status!);
        toast.error('Error while trying to start a transfer task');
      },
      ...config
    }
  );

export const useCancelTask = (config?: ConfigMutation) =>
  useMutation(
    ['cancelTask'],
    (payload: ICancelTask) => apiClient.post(ENDPOINTS.cancelTransferTasks, payload).then((res) => res.data),
    {
      onError: (error: AxiosError) => {
        verifyAuth(error.status!);
        toast.error('Error while trying to cancel a transfer task');
      },
      ...config
    }
  );

export const useSetCurrentFirmware = (config?: ConfigMutation) =>
  useMutation(
    ['setCurrentFirmware'],
    (payload: ISetCurrentFirmware) => apiClient.post(ENDPOINTS.setCurrentFirmware, payload).then((res) => res.data),
    {
      onError: (error: AxiosError) => {
        verifyAuth(error.status!);
        toast.error('Error while trying to set current firmware');
      },
      ...config
    }
  );
