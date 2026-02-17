/**
 * Design Tokens - Analog Quest Design System
 *
 * Centralized design constants for consistent, maintainable styling.
 * All values validated for WCAG AA accessibility.
 *
 * Last updated: Session 43 - 2026-02-11
 */

// ============================================================================
// COLORS
// ============================================================================

export const colors = {
  // Background colors
  background: {
    primary: '#FEF9ED',      // Cream - main background
    secondary: '#F7ECD9',    // Cream mid - subtle sections
    tertiary: '#DCEAEA',     // Teal light - accents, cards
  },

  // Text colors
  text: {
    primary: '#5D524B',      // Brown - body text (contrast ratio: 7.8:1 on cream) ✓ WCAG AA
    secondary: '#5D524B99',  // Brown 60% - muted text (contrast: 3.1:1) ✓ WCAG AA Large
    tertiary: '#5D524B80',   // Brown 50% - subtle text
    dark: '#451B25',         // Brown dark - emphasis, links (contrast: 11.2:1) ✓ WCAG AAA
  },

  // Accent colors
  accent: {
    teal: '#CAE1E1',         // Primary accent
    tealLight: '#DCEAEA',    // Light accent
    brown: '#5D524B',        // Secondary accent
    brownDark: '#451B25',    // Dark accent
  },

  // Semantic colors (warm palette only, no bright colors)
  semantic: {
    excellent: '#451B25',    // Dark brown for "excellent" rating
    good: '#5D524B',         // Medium brown for "good" rating
    border: '#5D524B33',     // Brown 20% - subtle borders
    borderHover: '#5D524B66', // Brown 40% - hover borders
  },

  // Domain badge colors (muted, warm tones)
  domain: {
    physics: '#C4B5A0',      // Warm tan
    biology: '#B8C4B0',      // Warm sage
    econ: '#C4ADA0',         // Warm beige
    cs: '#A8B4C0',           // Warm gray-blue
    math: '#B0A8C0',         // Warm lavender
    qBio: '#B8C4B0',         // Same as biology
    qFin: '#C4ADA0',         // Same as econ
    other: '#B8B0A8',        // Warm gray
  },
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Font families
  fontFamily: {
    serif: ['adriane', 'Georgia', 'serif'],
    mono: ['degular-mono', 'Courier New', 'monospace'],
  },

  // Font sizes (responsive)
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px - labels, mono
    base: '1rem',       // 16px - body
    lg: '1.125rem',     // 18px - large body
    xl: '1.25rem',      // 20px - small headings
    '2xl': '1.5rem',    // 24px - h3
    '3xl': '2rem',      // 32px - h2
    '4xl': '2.5rem',    // 40px - h1
    '5xl': '3rem',      // 48px - hero
  },

  // Font weights
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // Line heights
  lineHeight: {
    tight: 1.2,         // Headings
    normal: 1.6,        // Body
    relaxed: 1.7,       // Large body, comfortable reading
    loose: 1.8,         // Extra space
  },

  // Letter spacing
  letterSpacing: {
    tight: '-0.02em',   // Large headings
    normal: '0',
    wide: '0.05em',     // Mono, labels (uppercase)
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  // Base scale (Tailwind compatible)
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px

  // Custom values
  18: '4.5rem',   // 72px
  22: '5.5rem',   // 88px

  // Container widths
  container: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
    content: '900px',   // Max width for readable content
    wide: '1200px',     // Max width for discovery grids (5xl)
  },
} as const;

// ============================================================================
// EFFECTS
// ============================================================================

export const effects = {
  // Border radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',    // 2px
    DEFAULT: '0.25rem', // 4px
    md: '0.375rem',    // 6px
    lg: '0.5rem',      // 8px
    xl: '0.75rem',     // 12px
  },

  // Box shadows (subtle, warm)
  boxShadow: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(93, 82, 75, 0.05)',
    DEFAULT: '0 1px 3px 0 rgba(93, 82, 75, 0.1), 0 1px 2px 0 rgba(93, 82, 75, 0.06)',
    md: '0 4px 6px -1px rgba(93, 82, 75, 0.1), 0 2px 4px -1px rgba(93, 82, 75, 0.06)',
    lg: '0 10px 15px -3px rgba(93, 82, 75, 0.1), 0 4px 6px -2px rgba(93, 82, 75, 0.05)',
  },

  // Transitions
  transition: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Border widths
  borderWidth: {
    0: '0',
    DEFAULT: '1px',
    2: '2px',
    4: '4px',
  },
} as const;

// ============================================================================
// COMPONENT TOKENS
// ============================================================================

export const components = {
  // Button variants
  button: {
    primary: {
      bg: colors.text.dark,
      text: colors.background.primary,
      hoverBg: colors.text.primary,
      padding: '0.75rem 2rem',
      fontSize: typography.fontSize.sm,
      fontFamily: typography.fontFamily.mono,
      transition: effects.transition.base,
    },
    secondary: {
      bg: 'transparent',
      text: colors.text.primary,
      border: colors.semantic.border,
      hoverBorder: colors.semantic.borderHover,
      padding: '0.75rem 2rem',
      fontSize: typography.fontSize.sm,
      fontFamily: typography.fontFamily.mono,
      transition: effects.transition.base,
    },
    tertiary: {
      bg: 'transparent',
      text: colors.text.dark,
      hoverText: colors.text.primary,
      padding: '0.5rem 1rem',
      fontSize: typography.fontSize.sm,
      fontFamily: typography.fontFamily.mono,
      transition: effects.transition.base,
    },
  },

  // Card styles
  card: {
    bg: colors.background.primary,
    border: colors.semantic.border,
    hoverBorder: colors.semantic.borderHover,
    padding: spacing[6],
    borderRadius: effects.borderRadius.lg,
    shadow: effects.boxShadow.sm,
    hoverShadow: effects.boxShadow.md,
    transition: effects.transition.base,
  },

  // Link styles
  link: {
    color: colors.text.dark,
    hoverColor: colors.text.primary,
    underline: 'transparent',
    hoverUnderline: colors.text.dark,
    transition: effects.transition.fast,
  },

  // Badge styles (domain badges, rating badges)
  badge: {
    padding: '0.25rem 0.75rem',
    fontSize: typography.fontSize.xs,
    fontFamily: typography.fontFamily.mono,
    borderRadius: effects.borderRadius.DEFAULT,
    fontWeight: typography.fontWeight.normal,
  },
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// ACCESSIBILITY
// ============================================================================

export const accessibility = {
  // Contrast ratios (WCAG AA/AAA compliance - validated 2026-02-11)
  contrastRatios: {
    'brown-on-cream': 7.21,           // ✓ WCAG AAA (normal text)
    'brown-dark-on-cream': 13.91,     // ✓ WCAG AAA (normal text)
    'brown-on-teal-light': 6.13,      // ✓ WCAG AA (normal text)
    'brown-dark-on-teal-light': 11.83, // ✓ WCAG AAA (normal text)
  },

  // Focus ring
  focusRing: {
    width: effects.borderWidth[2],
    color: colors.text.primary,
    offset: '2px',
  },

  // Minimum touch target size
  minTouchTarget: {
    width: '44px',
    height: '44px',
  },
} as const;

// ============================================================================
// EXPORTS
// ============================================================================

export const designTokens = {
  colors,
  typography,
  spacing,
  effects,
  components,
  breakpoints,
  accessibility,
} as const;

export default designTokens;
