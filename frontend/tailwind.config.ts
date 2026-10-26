import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        garmin: {
          blue: "#00B0E7",
          dark: "#0A0F1C",
          card: "#111827",
          border: "#1F2937",
          accent: "#00B0E7",
        },
      },
    },
  },
  plugins: [],
};
export default config;
