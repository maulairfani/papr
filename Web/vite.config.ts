import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Tailwind v4 plugs straight into Vite (no postcss/tailwind.config.js needed).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true, // reachable from the Docker network when containerized
    port: 5173,
  },
});
