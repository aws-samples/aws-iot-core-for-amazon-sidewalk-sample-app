// Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svgr(), react()],
  css: {
    modules: {
      localsConvention: "camelCase",
    },
  },
  build: {
    outDir: "./build",
  },
  define: {
    global: {},
  },
  resolve: {
    alias: {
      "./runtimeConfig": "./runtimeConfig.browser",
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'https://mlxwxd261l.execute-api.us-east-1.amazonaws.com/dev',
        changeOrigin: true
      }
    }
  }
});
