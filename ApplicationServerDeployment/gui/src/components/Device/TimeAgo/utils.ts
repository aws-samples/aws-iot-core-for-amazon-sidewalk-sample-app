const DATE_UNITS = {
  day: 86400,
  hour: 3600,
  minute: 60,
  second: 1,
};

const getSecondsDiff = (timestamp: number) => (Date.now() - timestamp) / 1000;

const getUnitAndValueDate = (secondsElapsed: number) => {
  for (const [unit, secondsInUnit] of Object.entries(DATE_UNITS)) {
    if (secondsElapsed >= secondsInUnit || unit === "second") {
      const value = Math.floor(secondsElapsed / secondsInUnit) * -1;
      return { value, unit };
    }
  }
};

type TimeMap = {
  [key: string]: string;
};

const timeMap: TimeMap = {
  second: "s",
  minute: "m",
  hour: "h",
  day: "d",
  week: "w",
};

export const getTimeAgo = (timestamp: number) => {
  const secondsElapsed = getSecondsDiff(timestamp);
  const { value, unit } = getUnitAndValueDate(secondsElapsed) as {
    value: number;
    unit: string;
  };

  return `${Math.abs(value)}${timeMap[unit]} ago`;
};
