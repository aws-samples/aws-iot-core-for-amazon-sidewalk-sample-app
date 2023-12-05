// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { RcFile } from 'antd/es/upload';
import { ACCESS_TOKEN, UNAUTHORIZE } from './constants';
import { formatDuration, intervalToDuration } from 'date-fns';
import { ProvideAuth } from './hooks/useAuth';
import { ReactNode } from 'react';

export const verifyAuth = (statusCode: number) => {
  if (statusCode === 401 || statusCode === 403) {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.setItem(UNAUTHORIZE, 'true');
    window.location.reload();
  }
};

export const convertToBase64 = (file: RcFile) => {
  return new Promise((resolve, reject) => {
    const fileReader = new FileReader();
    fileReader.readAsDataURL(file);

    fileReader.onload = () => {
      resolve((fileReader.result as string).split(',')[1]);
    };

    fileReader.onerror = (error) => {
      reject(error);
    };
  });
};

export const getFileSize = (number: number) => {
  const oneMB = 1024;
  const oneGB = 1024 * 1024;

  if (number < oneMB) {
    return `${number} KB`;
  }

  if (number >= oneGB) {
    const calc = (number / oneGB).toFixed(1);
    return `${calc} GB`;
  }

  if (number >= oneMB) {
    const calc = (number / oneMB).toFixed(1);
    return `${calc} MB`;
  }

  return number;
};

export const showValueOrDash = (value: string | number) => value || '-';

export const getDurationString = ({ start, end }: { start: number | Date; end: number | Date }) => {
  if (!start || !end) {
    return '-';
  }
  const duration = intervalToDuration({ start, end });
  const durationAsString = formatDuration(duration);
  return <>{showValueOrDash(durationAsString)}</>;
};

export const withAuthProvider = (Component: ReactNode) => <ProvideAuth>{Component}</ProvideAuth>;
