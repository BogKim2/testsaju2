import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// Vite 설정
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // @/ 경로 별칭 설정
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",   // localhost + 127.0.0.1 모두 허용
    strictPort: true,
  },
});
