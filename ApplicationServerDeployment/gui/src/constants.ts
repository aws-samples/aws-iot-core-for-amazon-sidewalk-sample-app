// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export const SENSOR_UNIT = {
  CELSIUS: `${String.fromCharCode(176)}C`,
  FAHRENHEIT: `${String.fromCharCode(176)}F`,
  UNKNOWN: '-'
};

export const API_URL = '/api';

export const COLORS = {
  gray: 'rgb(255, 99, 132)'
};

export const LED_STATE = {
  ON: 'ON',
  OFF: 'OFF'
};

export const ACCESS_TOKEN = 'access_token';
export const UNAUTHORIZE = 'Unauthorize_error';
export const MOCK_MODE = import.meta.env.MODE === 'production' ? false : import.meta.env.VITE_MOCK_MODE === 'true';
