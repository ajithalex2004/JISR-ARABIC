/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#064e3b',    // UAE Deep Emerald
          primary: '#047857', // Emerald Green (NOT blue!)
          light: '#ecfdf5',   // Light mint tint
          accent: '#b45309',  // Desert Amber / Terracotta
          gold: '#d97706',    // Warm Sand Gold
          surface: '#fbfbfa', // High-trust educational warm white
          panel: '#ffffff',
          slate: '#0f172a',   // Deep charcoal text
          border: '#d1d5db',  // Crisp sharp border
        }
      },
      fontFamily: {
        arabic: ['"Noto Naskh Arabic"', 'Amiri', 'Tajawal', 'Cairo', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0px',
        none: '0px',
        sm: '0px',
        md: '0px',
        lg: '0px',
        xl: '0px',
        '2xl': '0px',
        full: '0px',
      }
    },
  },
  plugins: [],
}
