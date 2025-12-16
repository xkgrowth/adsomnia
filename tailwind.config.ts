import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Adsomnia Brand Colors
        background: "var(--color-bg-primary)",
        foreground: "var(--color-text-primary)",
        
        // Background shades
        "bg-primary": "var(--color-bg-primary)",
        "bg-secondary": "var(--color-bg-secondary)",
        "bg-tertiary": "var(--color-bg-tertiary)",
        "bg-elevated": "var(--color-bg-elevated)",
        
        // Text shades
        "text-primary": "var(--color-text-primary)",
        "text-secondary": "var(--color-text-secondary)",
        "text-muted": "var(--color-text-muted)",
        
        // Accent colors
        "accent-yellow": "var(--color-accent-yellow)",
        "accent-cyan": "var(--color-accent-cyan)",
        "accent-orange": "var(--color-accent-orange)",
        
        // Semantic
        success: "var(--color-success)",
        error: "var(--color-error)",
        warning: "var(--color-warning)",
        
        // Border
        border: "var(--color-border)",
        "border-hover": "var(--color-border-hover)",
        divider: "var(--color-divider)",
      },
      fontFamily: {
        headline: ["Bebas Neue", "Impact", "sans-serif"],
        body: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        hero: ["4rem", { lineHeight: "1.1" }],
        "display-1": ["2.5rem", { lineHeight: "1.1" }],
        "display-2": ["2rem", { lineHeight: "1.1" }],
        "display-3": ["1.5rem", { lineHeight: "1.2" }],
      },
      letterSpacing: {
        tighter: "-0.02em",
        wide: "0.05em",
        wider: "0.1em",
        widest: "0.15em",
      },
      borderRadius: {
        none: "0",
        sm: "2px",
        DEFAULT: "4px",
        // Adsomnia uses sharp corners - these are max values
      },
      transitionDuration: {
        fast: "150ms",
        normal: "300ms",
        slow: "500ms",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
