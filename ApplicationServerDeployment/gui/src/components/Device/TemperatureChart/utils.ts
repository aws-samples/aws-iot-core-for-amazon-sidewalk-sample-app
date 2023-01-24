// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { ChartData } from "chart.js";
import { COLORS } from "../../../constants";
import { IMeasurement } from "../../../types";

export const mapMeasurementsToChartData = (arr: IMeasurement[]) => {
  return {
    labels: arr.map((measurement) =>
      new Date(measurement.time).toLocaleTimeString()
    ),
    datasets: [
      {
        data: arr.map((measurement) => measurement.value),
        backgroundColor: COLORS.gray,
        type: "line",
        tension: 0.1,
      },
    ],
  } as ChartData<"line">;
};
