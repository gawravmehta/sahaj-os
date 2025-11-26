// vite.config.js

import { defineConfig } from "vite";
import path from "path";

// 1. Read the entry file path from the environment variable (set by generator.py)
//    It defaults to "src/cmp.js" for safety, but Python will override it.
const entryPath = process.env.BUILD_ENTRY || "src/cmp.js";

// 2. Read the desired output file name from the environment variable
const fileName = process.env.BUILD_FILE_NAME || "cmp-widget";

export default defineConfig({
  build: {
    lib: {
      // Use the dynamic path
      entry: path.resolve(__dirname, entryPath),
      name: "CMPWidget",
      // Use the dynamic file name (e.g., widget_one-cmp-widget)
      fileName: fileName,
      formats: ["iife"],
    },
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
});
