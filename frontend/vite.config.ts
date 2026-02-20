import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            // Forward API requests to the Python backend
            '/upload': 'http://127.0.0.1:8000',
            '/clusters': 'http://127.0.0.1:8000',
            '/insights': 'http://127.0.0.1:8000',
            '/download': 'http://127.0.0.1:8000',
        }
    }
})
