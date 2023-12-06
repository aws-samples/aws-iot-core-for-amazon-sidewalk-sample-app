import { DatePicker as AntdDatePicker, DatePickerProps } from 'antd';
import { useState } from 'react';
import { IStartTransferTask } from '../../../../types';
import dayjs from 'dayjs';

interface Props {
  onDatePickerChange: (date: DatePickerProps['value']) => void;
  dateValue: number | undefined;
}

export const DatePicker = ({ onDatePickerChange, dateValue }: Props) => {
  const range = (start: number, end: number) => {
    const result = [];
    for (let i = start; i < end; i++) {
      result.push(i);
    }
    return result;
  };

  const disabledDateTime = () => ({
    disabledHours: () => range(0, 24).splice(0, dayjs().hour()),
    disabledMinutes: () => range(0, 60).splice(0, dayjs().minute()),
    disabledSeconds: () => range(0, 60).splice(0, dayjs().second())
  });

  const disabledDate = (current: dayjs.Dayjs) => {
    // Can not select days before today and now
    return current && current < dayjs().startOf('day');
  };

  return (
    <AntdDatePicker
      showTime
      placeholder="Now"
      onChange={onDatePickerChange}
      format="YYYY-MM-DD HH:mm:ss"
      disabledDate={disabledDate}
      disabledTime={disabledDateTime}
      value={dateValue ? dayjs(dateValue) : undefined}
    />
  );
};
