export default {
  content: ['./src/**/*.{html,js,svelte,ts,md}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'Noto Sans TC', 'sans-serif'],
        display: ['Inter', 'Noto Sans TC', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        ink: { DEFAULT: '#0c0c0e', 50: '#f5f5f5', 100: '#e6e6e7', 200: '#cfcfd1', 300: '#adadaf', 400: '#848486', 500: '#6a6a6c', 600: '#545456', 700: '#464648', 800: '#3c3c3d', 900: '#353536', 950: '#0c0c0e' },
        slate: { DEFAULT: '#1e2330', 50: '#f0f1f4', 100: '#d9dce3', 200: '#b3b9c8', 300: '#868fa7', 400: '#606d8a', 500: '#48526d', 600: '#3a4259', 700: '#323849', 800: '#2c303e', 900: '#282b36', 950: '#1e2330' },
        gold: { DEFAULT: '#c8a84b', 50: '#fdf8ed', 100: '#f9efd1', 200: '#f2dda0', 300: '#e9c76b', 400: '#c8a84b', 500: '#b8913a', 600: '#9f7230', 700: '#85552a', 800: '#6f4529', 900: '#5f3b27', 950: '#371f13' },
        glass: {
          light: 'rgba(255,255,255,0.7)',
          dark: 'rgba(255,255,255,0.06)',
          border: 'rgba(255,255,255,0.1)',
          hover: 'rgba(255,255,255,0.12)',
        },
        accent: {
          blue: '#3b82f6',
          teal: '#14b8a6',
          amber: '#f59e0b',
        }
      },
      borderRadius: {
        glass: '16px',
        card: '12px',
        pill: '9999px',
      },
      backdropBlur: {
        glass: '20px',
      },
      boxShadow: {
        'glass': '0 4px 30px rgba(0,0,0,0.1)',
        'glass-lg': '0 8px 60px rgba(0,0,0,0.12)',
        'card': '0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)',
        'card-hover': '0 10px 30px rgba(0,0,0,0.08), 0 4px 8px rgba(0,0,0,0.04)',
        'elevation': '0 2px 8px rgba(0,0,0,0.12)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(20px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
      },
    }
  },
  plugins: []
};
