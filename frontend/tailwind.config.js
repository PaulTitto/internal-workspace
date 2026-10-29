// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        srkk: {
          DEFAULT: '#1226AA',
          50: '#F0F3FF',
          100: '#EEF2FF',
          200: '#DDE3FD',
          300: '#C7D2FE',
          400: '#8DA4F7',
          500: '#3D5BF6',
          600: '#1226AA',
          700: '#0E1F8C',
          800: '#0A1560',
          900: '#070D3D',
          dark: '#080E2F',
        },
      },
    },
  },
  plugins: [],
};
