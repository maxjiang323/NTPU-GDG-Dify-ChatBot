/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "/static/" : "/", // 生產模式下，靜態檔案的基礎路徑
  server: {
    host: "localhost",
    port: 8080,
  },
  plugins: [react()],
  resolve: {
    alias: {
      // 模組路徑別名
      "@": path.resolve(__dirname, "./src"), // 讓 import 時可以直接用 @/components/xxx 而不用 ../../../components/xxx
    },
  },
  test: {
    globals: true, // 讓測試檔不用每個都 import { describe, it, expect }，直接用即可
    environment: "jsdom", // 模擬瀏覽器環境（因為 Node.js 本身沒有 window/document 等 DOM 物件）
    setupFiles: "./src/test/setup.ts", // 測試前執行的設定檔
    reporters: ["default", "html"], // 測試報告
    outputFile: {
      html: "./test-report/index.html",
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      reportsDirectory: "./coverage",
    },
  },
  build: {
    outDir: "dist", // 輸出目錄
    sourcemap: mode === "development", // 開發模式產生 source map
    minify: mode === "production", // 生產模式壓縮
  },
  esbuild: {
    drop: mode === "production" ? ["console", "debugger"] : [], // 生產模式移除 console 和 debugger
  },
}));
