// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { Button, Card, Flex, Select } from 'antd';
import { useGetFileNames, useSetCurrentFirmware } from '../../../hooks/api/api';
import { useEffect, useState } from 'react';
import styles from '../styles.module.css';
import toast from 'react-hot-toast';

export const FirmwareConfig = () => {
  const { data: s3List, isLoading: isLoadingFilenames, refetch: refetchFilenames } = useGetFileNames();
  const { mutate: sendCurrentFirmare, isLoading: sendingCurrentFirmware } = useSetCurrentFirmware({
    onSuccess: () => {
      toast.success('Firmware has been set');
      setFilenameToDisplay('-');
      refetchFilenames();
    }
  });
  const [payload, setPayload] = useState({ fileName: '' });
  const [filenameToDisplay, setFilenameToDisplay] = useState('-');

  const handleFilenameSelected = (fileName: string) => {
    setPayload((prev) => ({ ...prev, fileName }));
  };

  const filterOption = (input: string, option?: { label: string; value: string }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase());

  const handleFirmwareClick = () => {
    sendCurrentFirmare({ filename: payload.fileName });
  };

  useEffect(() => {
    const currentFirmare = s3List?.current_firmware_file_name?.split('/')[1];
    setFilenameToDisplay(currentFirmare!);
  }, [s3List?.current_firmware_file_name]);

  useEffect(() => {
    if (!sendingCurrentFirmware) return;
    setFilenameToDisplay('-');
  }, [sendingCurrentFirmware]);

  return (
    <Card style={{ alignSelf: 'center', margin: '0 auto' }}>
      <div className={styles.titleFirmware}>
        Current Firmware: <span style={{ fontStyle: 'italic' }}>{filenameToDisplay}</span>
      </div>
      <p>The selected file will be sent when a device requests a Firmware Update OTA</p>
      <Flex gap="small" align="center">
        <Select
          showSearch
          placeholder="Select a file"
          optionFilterProp="children"
          onChange={handleFilenameSelected}
          style={{ minWidth: '200px' }}
          loading={isLoadingFilenames}
          disabled={isLoadingFilenames}
          filterOption={filterOption}
          options={s3List?.file_names.map((filename) => ({ label: filename, value: filename }))}
          value={payload.fileName || filenameToDisplay}
        />
        <Button
          type="primary"
          onClick={handleFirmwareClick}
          disabled={sendingCurrentFirmware || !payload.fileName}
          loading={sendingCurrentFirmware}
        >
          Set Current Firmware
        </Button>
      </Flex>
    </Card>
  );
};
