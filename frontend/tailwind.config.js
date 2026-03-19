/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f4f7ff",
          100: "#e8efff",
          500: "#3b5bdb",
          600: "#2f4ac2",
          700: "#263c9e",
        },
      },
      boxShadow: {
        glass: "0 10px 35px rgba(15, 23, 42, 0.18)",
      },
      fontFamily: {
        display: ["Poppins", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
}

