// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

export const logger = {
  log: (...data: any[]) =>
    import.meta.env.DEV ? console.log(...data) : undefined,
};
