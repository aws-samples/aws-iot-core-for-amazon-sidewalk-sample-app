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
  Cancelled: <GiCancel />,
  Failed: <BiSolidError />,
  Complete: <AiOutlineCheckCircle />,
  Completed: <AiOutlineCheckCircle />,
  Pending: <PiClock />,
  Transferring: <BiTransfer />,
  None: <AiOutlineDash />
};

export const TransferStatus = ({ type }: Props) => {
  const Icon = statusMap[type] || <></>;
  const colorClass = styles[`status${type}`];

  return (
    <span className={classNames(styles.container, colorClass)}>
      <>
        {Icon}
        {type}
      </>
    </span>
  );
};
