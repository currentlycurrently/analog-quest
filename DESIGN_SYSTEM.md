# Design System - Analog Quest

**Version**: 1.0
**Last Updated**: Session 43 - 2026-02-11
**Status**: Locked In ✓

---

## Overview

Analog Quest uses a warm, accessible, and restrained design system that conveys trust, seriousness, and intellectual rigor. The design language is intentionally minimal, avoiding bright colors, emojis, and generic tech aesthetics.

**Design Philosophy**:
- **Warm, not clinical**: Cream and brown palette instead of stark white/black
- **Accessible**: All color combinations meet WCAG AA standards (validated)
- **Restrained**: Spacious layouts, subtle accents, no visual noise
- **Typography-driven**: Serif for content (Adriane), monospace for interaction (Degular Mono)
- **Sustainable**: Centralized design tokens, scalable to 100+ sessions

---

## Color Palette

### Primary Colors

| Color | Hex | Use Case | Contrast on Cream |
|-------|-----|----------|-------------------|
| **Cream** | `#FEF9ED` | Primary background | — |
| **Brown** | `#5D524B` | Body text, headings | 7.21:1 ✓ WCAG AAA |
| **Brown Dark** | `#451B25` | Emphasis, links, buttons | 13.91:1 ✓ WCAG AAA |
| **Teal** | `#CAE1E1` | Accents, highlights | — |
| **Teal Light** | `#DCEAEA` | Subtle backgrounds, cards | — |

### Secondary Colors

| Color | Hex | Use Case |
|-------|-----|----------|
| **Cream Mid** | `#F7ECD9` | Subtle sections |
| **Cream Light** | `#FEF1C8` | Hover states |
| **Cream Warm** | `#F6E5B8` | Alternative backgrounds |

### Domain Badge Colors (Muted, Warm)

| Domain | Hex | Description |
|--------|-----|-------------|
| Physics | `#C4B5A0` | Warm tan |
| Biology | `#B8C4B0` | Warm sage |
| Economics | `#C4ADA0` | Warm beige |
| Computer Science | `#A8B4C0` | Warm gray-blue |
| Mathematics | `#B0A8C0` | Warm lavender |

---

## Typography

### Font Families

- **Serif (Adriane)**: Body text, headings, content
  `font-family: 'adriane', Georgia, serif`

- **Monospace (Degular Mono)**: Labels, buttons, navigation
  `font-family: 'degular-mono', 'Courier New', monospace`

### Type Scale

| Token | Size | Use Case |
|-------|------|----------|
| `xs` | 12px (0.75rem) | Small labels, badges |
| `sm` | 14px (0.875rem) | Monospace labels, buttons |
| `base` | 16px (1rem) | Body text |
| `lg` | 18px (1.125rem) | Large body text |
| `xl` | 20px (1.25rem) | Small headings |
| `2xl` | 24px (1.5rem) | H3 |
| `3xl` | 32px (2rem) | H2 |
| `4xl` | 40px (2.5rem) | H1 |
| `5xl` | 48px (3rem) | Hero text |

### Type Hierarchy

```css
h1: 40px (2.5rem), serif, bold, line-height 1.2, letter-spacing -0.02em
h2: 32px (2rem), serif, bold, line-height 1.2, letter-spacing -0.01em
h3: 24px (1.5rem), serif, bold, line-height 1.2
p:  16px (1rem), serif, normal, line-height 1.7
```

---

## Spacing

**Base Unit**: 4px (0.25rem)

| Token | Value | Use Case |
|-------|-------|----------|
| `1` | 4px | Tight spacing |
| `2` | 8px | Small gaps |
| `3` | 12px | Default gaps |
| `4` | 16px | Medium gaps |
| `6` | 24px | Card padding |
| `8` | 32px | Section gaps |
| `12` | 48px | Large gaps |
| `16` | 64px | XL gaps |
| `24` | 96px | Hero spacing |

### Container Widths

| Token | Value | Use Case |
|-------|-------|----------|
| `content` | 900px | Max width for readable text |
| `wide` | 1200px | Discovery grids (max-w-5xl) |

---

## Components

### Button

**Variants**: `primary`, `secondary`, `tertiary`
**Sizes**: `sm`, `md`, `lg`

```tsx
import Button from '@/components/Button';

// Primary button (dark background)
<Button variant="primary">view discoveries</Button>

// Secondary button (outlined)
<Button variant="secondary">learn more</Button>

// Tertiary button (text-only)
<Button variant="tertiary" as="link" href="/about">about</Button>
```

**Styles**:
- **Primary**: Dark brown background, cream text, hover: lighter brown
- **Secondary**: Transparent background, brown border, hover: darker border
- **Tertiary**: Text-only, brown-dark color, hover: brown

### Card

**Use Case**: Discovery cards, content blocks

```tsx
className="bg-cream border border-brown/20 hover:border-brown/40 p-6 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
```

### Badge (Domain, Rating)

**Use Case**: Domain labels, rating indicators

```tsx
className="px-3 py-1 text-xs font-mono rounded bg-[domain-color] text-brown-dark"
```

---

## Accessibility

### WCAG Compliance

All color combinations validated against WCAG AA standards (script: `scripts/validate_color_contrast.js`)

| Combination | Ratio | Standard |
|-------------|-------|----------|
| Brown on Cream | 7.21:1 | ✓ WCAG AAA |
| Brown Dark on Cream | 13.91:1 | ✓ WCAG AAA |
| Brown on Teal Light | 6.13:1 | ✓ WCAG AA |
| Brown Dark on Teal Light | 11.83:1 | ✓ WCAG AAA |

### Focus States

```css
focus:outline-none focus:ring-2 focus:ring-brown focus:ring-offset-2
```

### Minimum Touch Targets

- **Width**: 44px
- **Height**: 44px
- Applies to all interactive elements (buttons, links)

---

## Effects

### Shadows (Subtle, Warm)

```css
shadow-sm:  0 1px 2px 0 rgba(93, 82, 75, 0.05)
shadow:     0 1px 3px 0 rgba(93, 82, 75, 0.1)
shadow-md:  0 4px 6px -1px rgba(93, 82, 75, 0.1)
shadow-lg:  0 10px 15px -3px rgba(93, 82, 75, 0.1)
```

### Transitions

```css
fast: 150ms cubic-bezier(0.4, 0, 0.2, 1)
base: 200ms cubic-bezier(0.4, 0, 0.2, 1)
slow: 300ms cubic-bezier(0.4, 0, 0.2, 1)
```

### Border Radius

```css
sm:      2px
DEFAULT: 4px
md:      6px
lg:      8px
xl:      12px
```

---

## Usage Guidelines

### DO:
- ✓ Use design tokens from `lib/design-tokens.ts`
- ✓ Use Button component for all CTAs
- ✓ Maintain spacious layouts (generous padding/margin)
- ✓ Use serif for content, mono for interaction
- ✓ Test color contrast for any new combinations

### DON'T:
- ✗ Hardcode colors (use tokens)
- ✗ Use emojis anywhere
- ✗ Use bright colors (blue, red, green, yellow)
- ✗ Use generic tech aesthetics
- ✗ Create new button styles (use Button component)

---

## Implementation

### Import Design Tokens

```typescript
import { colors, typography, spacing, components } from '@/lib/design-tokens';

// Use in Tailwind classes
className="text-brown bg-cream px-6 py-3"

// Or use tokens directly in styled components
style={{ color: colors.text.primary, fontFamily: typography.fontFamily.serif }}
```

### Tailwind Config

Design tokens are also defined in `tailwind.config.ts` for Tailwind utility classes:

```typescript
colors: {
  cream: { DEFAULT: '#FEF9ED', light: '#FEF1C8', mid: '#F7ECD9', warm: '#F6E5B8' },
  brown: { DEFAULT: '#5D524B', dark: '#451B25' },
  teal: { DEFAULT: '#CAE1E1', light: '#DCEAEA' },
}
```

---

## Validation

### Color Contrast

Run validation script:

```bash
node scripts/validate_color_contrast.js
```

Expected output: All combinations pass WCAG AA ✓

### Build Test

```bash
npm run build
```

Expected output: 0 TypeScript errors, all pages generated ✓

---

## Future Considerations

### Scaling (50-100 discoveries)
- Pagination for discovery grid
- Lazy loading for images (if added)
- Virtual scrolling (if needed)

### Dark Mode (Not Current Priority)
- Invert palette: dark cream → dark brown, brown → light cream
- Maintain contrast ratios
- Add toggle in Navigation

### Internationalization (Not Current Priority)
- Font fallbacks for non-Latin scripts
- Adjust line-height for CJK characters

---

## References

- **Design Tokens**: `lib/design-tokens.ts`
- **Button Component**: `components/Button.tsx`
- **Tailwind Config**: `tailwind.config.ts`
- **Global Styles**: `app/globals.css`
- **Color Validation**: `scripts/validate_color_contrast.js`

---

**Questions or Issues?**
Document in `TECHNICAL_DEBT.md` or ask in `QUESTIONS.md`

**Last Reviewed**: Session 43 - 2026-02-11
**Next Review**: Session 50 (or when adding 50+ new discoveries)
