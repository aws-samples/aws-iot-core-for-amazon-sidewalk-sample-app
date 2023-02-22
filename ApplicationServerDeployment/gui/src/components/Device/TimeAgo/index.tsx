import { useEffect, useState } from "react"
import { getTimeAgo } from "./utils";

interface Props {
  date: number;
}

export const TimeAgo = ({ date }: Props) => {
  const [time, setTime] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(getTimeAgo(date));
    }, 1000);

    return () => clearInterval(interval);
  }, [date]);

  return (
    <div>{time}</div>
  )
}