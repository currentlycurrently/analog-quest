import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm, accessible palette
        cream: {
          DEFAULT: '#FEF9ED',
          light: '#FEF1C8',
          mid: '#F7ECD9',
          warm: '#F6E5B8',
        },
        teal: {
          light: '#DCEAEA',
          DEFAULT: '#CAE1E1',
        },
        brown: {
          DEFAULT: '#5D524B',
          dark: '#451B25',
        },
      },
      fontFamily: {
        serif: ['adriane', 'Georgia', 'serif'],
        mono: ['degular-mono', 'Courier New', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
    },
  },
  plugins: [],
} satisfies Config;
