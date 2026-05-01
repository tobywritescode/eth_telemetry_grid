import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  base: 'https://eth-telemetry-grid.vercel.app/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
});
