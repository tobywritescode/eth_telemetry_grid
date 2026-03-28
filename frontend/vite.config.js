import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  base: '/telemetry/', // Explicitly match your main site's sub-path
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
});
