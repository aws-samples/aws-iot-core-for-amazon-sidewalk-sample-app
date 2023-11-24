// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { RcFile } from "antd/es/upload";
import { ACCESS_TOKEN, UNAUTHORIZE } from "./constants";

export const verifyAuth = (statusCode: number) => {
  if (statusCode === 401 || statusCode === 403) {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.setItem(UNAUTHORIZE, "true");
    window.location.reload();
  }
};

export const convertToBase64 = (file: RcFile) => {
  return new Promise((resolve, reject) => {
    const fileReader = new FileReader();
    fileReader.readAsDataURL(file);

    fileReader.onload = () => {
      resolve(fileReader.result);
    };

    fileReader.onerror = (error) => {
      reject(error);
    };
  });
};
