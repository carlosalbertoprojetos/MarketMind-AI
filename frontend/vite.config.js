import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    testTimeout: 10000,
    hookTimeout: 10000,
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      // Encaminha /api/* para o backend em localhost:8000 (ex: /api/auth/login -> http://localhost:8000/auth/login)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
