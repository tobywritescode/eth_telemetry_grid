import { defineConfig } from 'vite';

export default defineConfig({
  root: './',
  base: './', // For correct asset paths on Vercel
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
});
