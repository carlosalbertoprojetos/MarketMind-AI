/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0b0b0f",
        haze: "#e7e3da",
        ember: "#e05a3b",
        moss: "#3c6f5d",
        smoke: "#15161d"
      },
      fontFamily: {
        display: ["'Space Grotesk'", "ui-sans-serif", "system-ui"],
        body: ["'Archivo'", "ui-sans-serif", "system-ui"]
      }
    }
  },
  plugins: []
};