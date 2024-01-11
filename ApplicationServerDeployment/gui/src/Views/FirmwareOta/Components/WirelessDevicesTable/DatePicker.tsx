// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { DatePicker as AntdDatePicker, DatePickerProps } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import { useCallback } from 'react';

interface Props {
  onDatePickerChange: (date: DatePickerProps['value']) => void;
  dateValue: number | undefined;
}

export const DatePicker = ({ onDatePickerChange, dateValue }: Props) => {
  // data range
  const minDate = dayjs().add(6, 'minutes');
  const maxDate = dayjs().add(48, 'hours');

  const getRange = (start: number, end: number) => [...Array(end - start + 1).keys()].map((i) => i + start);

  const disabledDate = useCallback(
    (d: Dayjs) => {
      if (d == null) {
        return null;
      }

      return (
        (minDate != null && d.isBefore(minDate) && !d.isSame(minDate, 'day')) ||
        (maxDate != null && d.isAfter(maxDate) && !d.isSame(maxDate, 'day'))
      );
    },
    [minDate, maxDate]
  );

  const disabledTime = useCallback(
    (d: Dayjs) => {
      if (d == null) {
        return null;
      }

      if (d.isSame(minDate, 'day')) {
        return {
          disabledHours: () => (minDate.hour() > 0 ? getRange(0, minDate.hour() - 1) : []),
          disabledMinutes: (hour: number) =>
            hour === minDate.hour() && minDate.minute() > 0 ? getRange(0, minDate.minute() - 1) : []
        };
      }

      if (d.isSame(maxDate, 'day')) {
        return {
          disabledHours: () => getRange(maxDate.hour() + 1, 24),
          disabledMinutes: (hour: number) => (hour === maxDate.hour() ? getRange(maxDate.minute() + 1, 60) : [])
        };
      }

      return null;
    },
    [minDate, maxDate]
  );

  return (
    <AntdDatePicker
      showTime
      placeholder="Now + 6 minutes"
      onChange={onDatePickerChange}
      format="YYYY-MM-DD HH:mm:ss"
      disabledDate={disabledDate as any}
      disabledTime={disabledTime as any}
      value={dateValue ? dayjs(dateValue) : undefined}
    />
  );
};
