import { useMutation, useQuery, UseMutationOptions } from 'react-query';
import { apiClient } from '../../apiClient';
import { ENDPOINTS } from '../../endpoints';
import { IFilenames, IStartTransferTask, ITransferTasks, IWirelessDevices } from '../../types';
import { UploadFile } from 'antd/es/upload/interface';
import toast from 'react-hot-toast';
import { verifyAuth } from '../../utils';
import { AxiosError } from 'axios';

export const useGetWirelessDevices = () =>
  useQuery<IWirelessDevices, AxiosError>(
    ['getWirelessDevices'],
    () => apiClient.get(ENDPOINTS.otaDevices).then((res) => res.data),
    {
      cacheTime: Infinity,
      onError: (error) => {
        console.log('error fetching', error);
        verifyAuth(error.status!);
        toast.error('Error fetching Wireless Devices');
      }
    }
  );

export const useGetTransferTasks = () =>
  useQuery<ITransferTasks, AxiosError>(['getTransferTasks'], () => apiClient.get(ENDPOINTS.tasks).then((res) => res.data), {
    cacheTime: Infinity,
    onError: (error) => {
      verifyAuth(error.status!);
      toast.error('Error fetching Transfer Tasks');
    }
  });

export const useS3Upload = () =>
  useMutation(['upload'], (payload: UploadFile) => apiClient.post(ENDPOINTS.upload, payload).then((res) => res.data), {
    retry: false,
    onError: (error: AxiosError) => {
      verifyAuth(error.status!);
      toast.error('Error while trying to upload a file');
    },
    onSuccess: () => {
      toast.success('File Uploaded');
    }
  });

export const useGetFileNames = () =>
  useQuery<IFilenames, AxiosError>(['getFilenames'], () => apiClient.get(ENDPOINTS.s3Filenames).then((res) => res.data), {
    cacheTime: Infinity,
    onError: (error) => {
      verifyAuth(error.status!);
      toast.error('Error getting filenames');
    }
  });

export const useStartTransferTask = (
  config?: Omit<UseMutationOptions<{}, AxiosError, {}, {}>, 'mutationKey' | 'mutationFn'>
) =>
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
