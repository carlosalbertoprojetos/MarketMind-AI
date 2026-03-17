/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        haze: "rgb(var(--color-haze) / <alpha-value>)",
        ember: "rgb(var(--color-accent) / <alpha-value>)",
        moss: "rgb(var(--color-accent-2) / <alpha-value>)",
        smoke: "rgb(var(--color-contrast) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        "surface-2": "rgb(var(--color-surface-2) / <alpha-value>)",
        "surface-3": "rgb(var(--color-surface-3) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        "border-strong": "rgb(var(--color-border-strong) / <alpha-value>)",
        muted: "rgb(var(--color-muted) / <alpha-value>)",
        "muted-2": "rgb(var(--color-muted-2) / <alpha-value>)",
        success: "rgb(var(--color-success) / <alpha-value>)",
        warning: "rgb(var(--color-warning) / <alpha-value>)",
        "on-accent": "rgb(var(--color-on-accent) / <alpha-value>)"
      },
      fontFamily: {
        display: ["'Space Grotesk'", "ui-sans-serif", "system-ui"],
        body: ["'Archivo'", "ui-sans-serif", "system-ui"]
      }
    }
  },
  plugins: []
};
