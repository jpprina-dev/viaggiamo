/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // ── Ruta Gaucha — Primary (Verde) ────────────────────────────────
        primary: {
          DEFAULT: '#006d33',
          // Numeric scale remapped to Ruta Gaucha tones (backward compat)
          50:  '#f5f2ff', // surface-container-low (lavender)
          100: '#e9e6f5', // surface-container-high
          200: '#d4d0f0',
          300: '#74dc8e', // primary-fixed-dim
          400: '#7ce495', // primary-container (CTA mint)
          500: '#006d33',
          600: '#006d33',
          700: '#005225', // on-primary-fixed-variant
          800: '#003919',
          900: '#00210b', // on-primary-fixed
          950: '#001005',
          // Named tokens (preferred for new components)
          container:          '#7ce495',
          'on-container':     '#00662f',
          fixed:              '#90f9a8',
          'fixed-dim':        '#74dc8e',
          'on-fixed':         '#00210b',
          'on-fixed-variant': '#005225',
        },

        // ── Secondary (Teal) ─────────────────────────────────────────────
        secondary: {
          DEFAULT: '#006a64',
          container:          '#96f3e9',
          fixed:              '#96f3e9',
          'fixed-dim':        '#7ad6cd',
          'on-container':     '#00716a',
          'on-fixed':         '#00201e',
          'on-fixed-variant': '#00504b',
          50:  '#f0fdfa',
          100: '#ccfbf1',
          200: '#96f3e9',
          300: '#7ad6cd',
          400: '#4abfb7',
          500: '#006a64',
          600: '#006a64',
          700: '#005754',
          800: '#00423f',
          900: '#00201e',
        },

        // ── Tertiary (Naranja / Madera) ──────────────────────────────────
        tertiary: {
          DEFAULT:        '#8e4e14',
          container:      '#ffc295',
          fixed:          '#ffdcc4',
          'fixed-dim':    '#ffb780',
          'on-container': '#86480c',
          'on-fixed':     '#2f1400',
          'on-fixed-variant': '#6f3800',
        },

        // ── Anchor Dark (Hero / Nav) ─────────────────────────────────────
        'anchor-dark': '#21212b',

        // ── Surface Hierarchy ────────────────────────────────────────────
        surface: {
          DEFAULT:             '#fcf8ff',
          dim:                 '#dbd8e6',
          bright:              '#fcf8ff',
          'container-lowest':  '#ffffff',
          'container-low':     '#f5f2ff',
          container:           '#efecfa',
          'container-high':    '#e9e6f5',
          'container-highest': '#e3e1ef',
        },

        // ── On-Surface ───────────────────────────────────────────────────
        'on-surface':         '#1b1b24',
        'on-surface-variant': '#3e4a3f',

        // ── Outline ──────────────────────────────────────────────────────
        outline:          '#6e7a6e',
        'outline-variant': '#becabc',

        // ── Inverse ──────────────────────────────────────────────────────
        'inverse-surface':    '#302f3a',
        'inverse-on-surface': '#f2effd',
        'inverse-primary':    '#74dc8e',

        // ── Error ────────────────────────────────────────────────────────
        error: {
          DEFAULT:      '#ba1a1a',
          container:    '#ffdad6',
          'on-container': '#93000a',
        },

        // ── shadcn/ui compatibility ───────────────────────────────────────
        background: '#fcf8ff',
        foreground: '#1b1b24',
        card: {
          DEFAULT:    '#ffffff',
          foreground: '#1b1b24',
        },
        muted: {
          DEFAULT:    '#f5f2ff',
          foreground: '#3e4a3f',
        },
        accent: {
          DEFAULT:    '#ffc295',
          foreground: '#86480c',
        },
        destructive: {
          DEFAULT:    '#ba1a1a',
          foreground: '#ffffff',
        },
        border:  '#becabc',
        input:   '#e9e6f5',
        ring:    '#7ce495',
        popover: {
          DEFAULT:    '#ffffff',
          foreground: '#1b1b24',
        },
      },

      // ── Border Radius ─────────────────────────────────────────────────
      borderRadius: {
        none:    '0',
        sm:      '0.375rem',   //  6 px
        DEFAULT: '0.75rem',    // 12 px
        md:      '0.75rem',    // 12 px – Inputs
        lg:      '1rem',       // 16 px – Cards
        xl:      '1.5rem',     // 24 px – Buttons, panels
        '2xl':   '2rem',       // 32 px – Modals
        '3xl':   '2.5rem',
        full:    '9999px',
      },

      // ── Typography ────────────────────────────────────────────────────
      fontFamily: {
        sans: ['var(--font-plus-jakarta-sans)', 'system-ui', 'sans-serif'],
      },

      fontSize: {
        'display-lg': ['3.5rem',   { lineHeight: '1.1',  fontWeight: '700' }],
        'display-md': ['2.75rem',  { lineHeight: '1.15', fontWeight: '700' }],
        'display-sm': ['2.25rem',  { lineHeight: '1.2',  fontWeight: '700' }],
        'headline-lg': ['2rem',    { lineHeight: '1.2',  fontWeight: '700' }],
        'headline-md': ['1.75rem', { lineHeight: '1.25', fontWeight: '700' }],
        'headline-sm': ['1.5rem',  { lineHeight: '1.3',  fontWeight: '700' }],
        'title-lg':  ['1.25rem',   { lineHeight: '1.4',  fontWeight: '700' }],
        'title-md':  ['1.125rem',  { lineHeight: '1.4',  fontWeight: '700' }],
        'title-sm':  ['1rem',      { lineHeight: '1.4',  fontWeight: '700' }],
        'body-lg':   ['1rem',      { lineHeight: '1.6',  fontWeight: '400' }],
        'body-md':   ['0.875rem',  { lineHeight: '1.6',  fontWeight: '400' }],
        'body-sm':   ['0.75rem',   { lineHeight: '1.5',  fontWeight: '400' }],
        'label-lg':  ['0.875rem',  { lineHeight: '1.4',  fontWeight: '700' }],
        'label-md':  ['0.75rem',   { lineHeight: '1.4',  fontWeight: '700' }],
        'label-sm':  ['0.6875rem', { lineHeight: '1.3',  fontWeight: '700' }],
      },

      // ── Shadows (Ambient — Ruta Gaucha) ──────────────────────────────
      boxShadow: {
        ambient:      '0 8px 28px 0 rgba(27,27,36,0.06)',
        'ambient-lg': '0 12px 40px 0 rgba(27,27,36,0.09)',
        glass:        '0 4px 24px 0 rgba(27,27,36,0.08)',
      },

      // ── Animations ────────────────────────────────────────────────────
      animation: {
        'fade-in':   'fadeIn 0.5s ease-in-out',
        'slide-up':  'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in':  'scaleIn 0.2s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%':   { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',    opacity: '1' },
        },
        slideDown: {
          '0%':   { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',     opacity: '1' },
        },
        scaleIn: {
          '0%':   { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)',    opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
