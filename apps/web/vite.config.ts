import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // 固定端口便于毕业设计演示脚本和截图流程复用。
    port: 5173
  }
});
