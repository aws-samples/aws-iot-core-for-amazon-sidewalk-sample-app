import { useQuery } from "react-query";
import { apiClient } from "../../apiClient";
import { ENDPOINTS } from "../../endpoints";
import { Response } from "redaxios";
import { IWirelessDevices } from "../../types";

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