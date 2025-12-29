/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
};
