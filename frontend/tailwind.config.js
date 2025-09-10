module.exports = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5fbff",
          100: "#e6f4ff",
          500: "#0ea5e9",
          700: "#0284c7",
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
