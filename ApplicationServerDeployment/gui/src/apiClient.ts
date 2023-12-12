// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios, { AxiosError, AxiosInstance } from 'axios';
import { ACCESS_TOKEN, API_URL } from './constants';
import { verifyAuth } from './utils';

// @ts-ignore
let instance: AxiosInstance;

const gateway = () => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN);
  const options = {
    baseURL: API_URL,
    ...(accessToken
      ? {
          headers: {
            authorizationtoken: `Basic ${accessToken}`
          }
        }
      : {})
  };

  instance = axios.create(options);

  // interceptors config
  instance.interceptors.response.use(
    (response) => response.data,
    (error: AxiosError) => {
      verifyAuth(error.response?.status);
      return Promise.reject(error);
    }
  );

  return instance;
};

export const setAuthHeader = (token: string) => {
  instance.defaults.headers['authorizationtoken'] = `Basic ${token}`;

  localStorage.setItem(ACCESS_TOKEN, token);
};

export const setUsernameHeader = (username: string) => {
  instance.defaults.headers['Username'] = `${username}`;
};

export const apiClient = gateway();
