import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Conexión directa con la API (VITE_API_URL); sin proxy.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
});
