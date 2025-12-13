import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
var isDebug = process.env.DEBUG_BUILD === 'true';
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    build: {
        minify: isDebug ? false : 'esbuild',
        sourcemap: isDebug ? 'inline' : false,
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
});
