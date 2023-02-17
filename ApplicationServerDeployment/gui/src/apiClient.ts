// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "redaxios";
import { ACCESS_TOKEN, API_URL } from "./constants";

// @ts-ignore
let instance;

const gateway = () => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN);
  const options = {
    baseURL: API_URL,
    ...(accessToken
      ? {
          headers: {
            Authorization: `Basic ${accessToken}`,
          },
        }
      : {}),
  };

  instance = axios.create(options);

  return instance;
};

export const setAuthHeader = (token: string) => {
  // @ts-ignore
  instance.defaults.headers = {
    Authorization: `Basic ${token}`,
  };

  localStorage.setItem(ACCESS_TOKEN, token);
};

export const apiClient = gateway();
