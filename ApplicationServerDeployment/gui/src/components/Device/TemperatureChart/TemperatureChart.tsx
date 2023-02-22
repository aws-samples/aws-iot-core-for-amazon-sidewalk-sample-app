// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import {
  Chart as ChartJS,
  ChartData,
  ChartOptions,
  Legend,
  LinearScale,
  PointElement,
  CategoryScale,
  LineElement,
  Tooltip,
} from "chart.js";
import { useEffect, useRef, useState } from "react";
import { Line } from "react-chartjs-2";
import { APP_CONFIG } from "../../../appConfig";
import { COLORS, SENSOR_UNIT } from "../../../constants";
import { ENDPOINTS, interpolateParams } from "../../../endpoints";
import useIsMobile from "../../../hooks/useIsMobile";
import { IMeasurement } from "../../../types";
import { mapMeasurementsToChartData } from "./utils";
import "./styles.css";
import { logger } from "../../../utils/logger";
import { apiClient } from "../../../apiClient";
import { verifyAuth } from "../../../utils";

ChartJS.register(
  LinearScale,
  CategoryScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend
);

interface Props {
  deviceId: string;
  sensorUnit: "CELSIUS" | "FAHRENHEIT" | "UNKNOWN";
  isSensorOn: boolean;
}

export const TemperatureChart = ({
  deviceId,
  sensorUnit,
  isSensorOn,
}: Props) => {
  const [values, setValues] = useState({
    datasets: [
      {
        data: [],
        backgroundColor: COLORS.gray,
      },
    ],
  } as ChartData<"line">);
  const [isLoading, setIsLoading] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [hasError, setHasError] = useState(false);
  const isDesktop = !useIsMobile();
  const SCALE_OFFSET = 0.5;
  const intervalMeasurementsId = useRef(0);

  const fetchMeasurements = async () => {
    try {
      const response = await apiClient.get<IMeasurement[]>(
        interpolateParams(ENDPOINTS.measurement, { id: deviceId })
      );

      setHasError(false);
      logger.log("Measurement", deviceId, { response: response.data });
      setValues(mapMeasurementsToChartData(response.data));
    } catch (error) {
      // @ts-ignore
      verifyAuth(error.status);
      logger.log("error fetching measurements");
      setHasError(true);
    }
  };

  const fetchMeasurementsWithLoading = async () => {
    setIsLoading(true);
    await fetchMeasurements();
    setIsLoading(false);
  };

  useEffect(() => {
    if (isSensorOn && isFirstLoad && !isLoading) {
      fetchMeasurementsWithLoading();
    }
  }, [isSensorOn]);

  useEffect(() => {
    if (isFirstLoad) return;

    intervalMeasurementsId.current = window.setInterval(
      fetchMeasurements,
      APP_CONFIG.intervals.measurement
    );

    return () => clearInterval(intervalMeasurementsId.current);
  }, [isFirstLoad, isSensorOn]);

  useEffect(() => {
    setIsFirstLoad(hasError);

    if (hasError) {
      clearInterval(intervalMeasurementsId.current);
    }
  }, [hasError]);

  const options: ChartOptions<"line"> = {
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) =>
            `${Number(context.raw).toFixed(1)}${SENSOR_UNIT[sensorUnit]}`,
        },
      },
    },
    scales: {
      y: {
        ticks: {
          callback: function (value) {
            return `${Number(value).toFixed(1)}${SENSOR_UNIT[sensorUnit]}`;
          },
        },
        min: isDesktop
          ? Math.min(...(values.datasets[0].data as number[])) - SCALE_OFFSET
          : undefined,
        max: isDesktop
          ? Math.max(...(values.datasets[0].data as number[])) + SCALE_OFFSET
          : undefined,
      },
    },
  };

  if (hasError) {
    return (
      <div className="flex-abs-center chart-section">
        Error loading measurements,{" "}
        <div
          role="button"
          className="chart-wrapper-link"
          onClick={fetchMeasurementsWithLoading}
        >
          try again
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-abs-center chart-section">
        Loading measurements...
      </div>
    );
  }

  if (!isSensorOn) {
    return (
      <div className="flex-abs-center chart-section">Sensor unavailable</div>
    );
  }

  if (values.datasets[0].data.length === 0) {
    return (
      <div className="flex-abs-center chart-section">No data to display</div>
    );
  }

  return (
    <div className="flex-abs-center chart-section">
      <Line datasetIdKey="line-chart" options={options} data={values} />
    </div>
  );
};
