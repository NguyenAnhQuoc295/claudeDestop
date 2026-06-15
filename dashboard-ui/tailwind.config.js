/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        surface: {
          50: '#fcfaf7', // Warm Cream background
          100: '#f6f2eb', // Warm Sand light
          200: '#ebdcc5', // Light warm border
          300: '#dfc7ab', // Medium warm border
          400: '#9b7f61', // Soft warm brown-gray
          500: '#7d6148', // Warm brown medium
          600: '#644e3b', // Warm brown dark
          700: '#4e3b2e', // Dark warm brown
          800: '#3a2d24', // Near black warm
          900: '#2b211a', // Black warm
          950: '#1c1511',
        },
        prompt: {
          chat: '#2563eb', // Deeper blue for contrast
          cowork: '#7c3aed', // Deeper purple for contrast
          code: '#059669', // Deeper emerald for contrast
        },
        accent: '#e06f53', // Soft Terracotta
      },
      animation: {
        'slide-in': 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-out': 'slideOut 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in': 'fadeIn 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'donut-draw': 'donutDraw 1s ease-out forwards',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(100%)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
        slideOut: {
          '0%': { transform: 'translateX(0)', opacity: 1 },
          '100%': { transform: 'translateX(100%)', opacity: 0 },
        },
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: 0, transform: 'scale(0.95)' },
          '100%': { opacity: 1, transform: 'scale(1)' },
        },
        donutDraw: {
          '0%': { strokeDashoffset: '251.2' },
          '100%': { strokeDashoffset: '0' },
        },
      },
    },
  },
  plugins: [],
}
