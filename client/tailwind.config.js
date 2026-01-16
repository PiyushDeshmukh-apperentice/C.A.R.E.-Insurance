/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
      },
      colors: {
        sureva: {
          blue: "#DBF4FF",
          "dark-blue": "#0C204B",
          green: "#3DB68A",
          "green-light": "rgba(61, 182, 138, 0.26)",
          orange: "#F99853",
          "orange-light": "rgba(249, 152, 83, 0.26)",
          gray: "#474747",
          "light-gray": "#F1F4F8",
          "card-bg": "#F2FBFF",
          pink: "#FFC0CB",
        },
      },
    },
  },
  plugins: [],
}
