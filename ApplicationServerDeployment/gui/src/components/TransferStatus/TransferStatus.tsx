// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import styles from './styles.module.css';
import { GiCancel } from 'react-icons/gi';
import { AiOutlineDash, AiOutlineCheckCircle } from 'react-icons/ai';
import { BiSolidError, BiTransfer } from 'react-icons/bi';
import { PiClock } from 'react-icons/pi';

import type { TransferStatusType } from '../../types';
import classNames from 'classnames';

interface Props {
  type: TransferStatusType;
}

const statusMap: { [K in TransferStatusType]: React.ReactNode } = {
  CANCELLED: <GiCancel />,
  FAILED: <BiSolidError />,
  COMPLETE: <AiOutlineCheckCircle />,
  COMPLETED: <AiOutlineCheckCircle />,
  PENDING: <PiClock />,
  TRANSFERRING: <BiTransfer />,
  NONE: <AiOutlineDash />
};

export const TransferStatus = ({ type }: Props) => {
  if (!type) return <></>;
  const Icon = statusMap[type] || <></>;
  const colorClass = styles[`status-${type.toLowerCase()}`];

  return (
    <span className={classNames(styles.container, colorClass)}>
      <>
        {Icon}
        {type}
      </>
    </span>
  );
};
