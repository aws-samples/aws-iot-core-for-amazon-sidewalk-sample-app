import { useQuery } from "react-query";
import { apiClient } from "../../apiClient";
import { ENDPOINTS } from "../../endpoints";
import { ITransferTasks, IWirelessDevices } from "../../types";

export const useGetWirelessDevices = () =>
  useQuery<IWirelessDevices>(
    ['getWirelessDevices'],
    () => apiClient.get(ENDPOINTS.mockDevices).then(res => res.data),
    {
      cacheTime: Infinity,
      onError: (err) => {
        console.log('error fetching', err)
      },
    }
  );

  export const useGetTransferTasks = () =>
  useQuery<ITransferTasks>(
    ['getTransferTasks'],
    () => apiClient.get(ENDPOINTS.mockTask).then(res => res.data),
    {
      cacheTime: Infinity,
      onError: (err) => {
        console.log('error fetching', err)
      },
    }
  );