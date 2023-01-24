// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import axios from "redaxios"
import { API_URL } from "./constants"

const gateway = () => {
  const instance = axios.create({
    baseURL: API_URL,
  });

  return instance;
}

export const apiClient = gateway();