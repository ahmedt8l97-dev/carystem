import { defineConfig } from 'vite';

export default defineConfig({
    root: 'web-frontend',
    server: {
        port: 3000,
        proxy: {
            '/api': 'http://localhost:8000', // Backward compat if needed
        },
        fs: {
            allow: ['..']
        }
    },
    build: {
        outDir: '../dist',
        emptyOutDir: true,
    }
});
