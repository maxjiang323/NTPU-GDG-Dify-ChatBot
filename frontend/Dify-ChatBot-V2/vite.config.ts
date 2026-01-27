/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === "production" ? "/static/" : "/",
  server: {
    host: "localhost",
    port: 8080,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
  build: {
    outDir: "dist",
    sourcemap: mode === "development",
    minify: mode === "production",
  },
  esbuild: {
    drop: mode === "production" ? ["console", "debugger"] : [],
  },
}));
