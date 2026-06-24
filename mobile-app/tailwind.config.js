/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#0f172a',
          primary: '#3b82f6',
          accent: '#ef4444',
          card: '#1e293b'
        }
      }
    },
  },
  plugins: [],
}
