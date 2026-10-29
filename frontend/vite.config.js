// frontend/vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // Serve index.html for all routes (SPA fallback) so /share/<token> works
    historyApiFallback: true,
  },
});
