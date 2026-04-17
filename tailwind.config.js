export default {
  content: ['./src/**/*.{html,js,svelte,ts,md}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Noto Sans TC', 'sans-serif'],
      },
      colors: {
        brand: {
          gold: '#c8a84b',
          ink: '#0c0c0e',
          slate: '#1e2330',
        }
      }
    }
  },
  plugins: []
};
