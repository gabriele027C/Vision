import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // 5173 è la porta default di Vite: la PWA wedding (WebAppPhotoSharing) ha un
    // service worker registrato su quell'origine — il browser mostrerebbe l'app sbagliata.
    host: "127.0.0.1",
    port: 5174,
    strictPort: true,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
