// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { defineConfig, loadEnv, ConfigEnv } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import { viteMockServe } from "vite-plugin-mock";

// https://vitejs.dev/config/
export default ({ mode }: ConfigEnv) => {
  process.env = { ...process.env, ...loadEnv(mode, process.cwd()) };

  return defineConfig({
    plugins: [
      svgr(),
      react(),
      viteMockServe({
        mockPath: "mock",
        enable: mode === "development",
      }),
    ],
    css: {
      modules: {
        localsConvention: "camelCase",
      },
    },
    build: {
      outDir: "./build",
    },
    define: {
      global: 'globalThis',
    },
    resolve: {
      alias: {
        "./runtimeConfig": "./runtimeConfig.browser",
      },
    },
    server: {
      proxy: {
        "/api": {
          target: process.env.VITE_API_URL,
          changeOrigin: true,
        },
      },
    },
  });
};
