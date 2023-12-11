import { ReactNode, createContext, useContext, useRef, useState } from 'react';
import { APP_CONFIG } from '../../../appConfig';
import { ITransferTasks, IWirelessDevices } from '../../../types';
import scrollIntoView from 'scroll-into-view';
import { ANTD_TABLE_HOVER_COLOR_VAR_NAME } from '../../../constants';

type TableType = 'tasks' | 'devices';

const scrollContext = createContext({
  setItemsDisposition: (items: ITransferTasks | IWirelessDevices, tableType: TableType) => {},
  scrollTo: (_id: string, _tableType: TableType) => {},
  tables: {
    devices: {
      pageSize: APP_CONFIG.ota.tables.devices.pageSize,
      idsList: {}
    },
    tasks: {
      pageSize: APP_CONFIG.ota.tables.tasks.pageSize,
      idsList: {}
    }
  },
  pageIndex: {
    devices: 1,
    tasks: 1
  },
  setPageIndex: (_page: number, _tableType: TableType) => {}
});

export const useRowScroller = () => useContext(scrollContext);

const useScrollProvider = () => {
  const tables = useRef({
    devices: {
      pageSize: APP_CONFIG.ota.tables.devices.pageSize,
      idsList: ['']
    },
    tasks: {
      pageSize: APP_CONFIG.ota.tables.tasks.pageSize,
      idsList: ['']
    }
  });
  const [pageIndex, setPageIndexInternal] = useState({
    devices: 1,
    tasks: 1
  });

  const setPageIndex = (page: number, tableType: TableType) => {
    setPageIndexInternal((previousValues) => ({ ...previousValues, [tableType]: page }));
  };

  const scrollTo = (id: string, tableType: TableType) => {
    const indexOfItem = tables.current[tableType].idsList.findLastIndex((item) => item === id);

    // no item found to scroll
    if (indexOfItem === -1) return;

    const pageIndexCalc = Math.ceil((indexOfItem + 1) / tables.current[tableType].pageSize);

    setPageIndex(pageIndexCalc, tableType);

    // we wait a cycle until DOM element is present
    setTimeout(() => {
      const element = document.querySelector(`[data-row-key="${id}"]`) as HTMLElement;

      if (!element) return;

      const rootElement = document.querySelector(':root') as HTMLElement;

      scrollIntoView(
        element,
        {
          align: {
            lockX: true
          }
        },
        (type) => {
          if (type === 'complete') {
            // forcing antd table style to disable hover color for a while because 
            // it interferes with highlight-row class effect
            rootElement?.style.setProperty(ANTD_TABLE_HOVER_COLOR_VAR_NAME, 'none');
            element?.classList.add('highlight-row');
            setTimeout(() => {
              element?.classList.remove('highlight-row');
              // puttinh back hover color to antd table after removing highlight
              rootElement?.style.setProperty(ANTD_TABLE_HOVER_COLOR_VAR_NAME, '#fafafa');
            }, 1000);
          }
        }
      );
    }, 0);
  };

  const setItemsDisposition = (items: ITransferTasks | IWirelessDevices, tableType: TableType) => {
    if (tableType === 'devices') {
      tables.current[tableType].idsList = (items as IWirelessDevices).wireless_devices.map((device) => device.device_id);
    } else if (tableType === 'tasks') {
      tables.current[tableType].idsList = (items as ITransferTasks).transfer_tasks.map((task) => task.task_id);
    }
  };

  return {
    setItemsDisposition,
    scrollTo,
    tables: tables.current,
    pageIndex,
    setPageIndex
  };
};

export const ScrollProvider = ({ children }: { children: ReactNode }) => {
  const value = useScrollProvider();

  return <scrollContext.Provider value={value}>{children}</scrollContext.Provider>;
};
