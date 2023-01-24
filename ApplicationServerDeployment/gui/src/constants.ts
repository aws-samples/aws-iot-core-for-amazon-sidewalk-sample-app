// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export const SENSOR_UNIT = {
  CELSIUS: `${String.fromCharCode(176)}C`,
  FAHRENHEIT: `${String.fromCharCode(176)}F`,
  UNKNOWN: "-",
};

export const API_URL = import.meta.env.VITE_API_URL;

export const COLORS = {
  gray: "rgb(255, 99, 132)",
}

export const LED_STATE = {
  ON: "ON",
  OFF: "OFF"
}
