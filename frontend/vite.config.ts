import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Datoteke na Windows so v kontejnerju priklopljene prek omrežne datoteke in dogodkov
    // o spremembah ni, zato jih Vite redno preverja (polling).
    watch: { usePolling: true, interval: 300 },
  },
})
