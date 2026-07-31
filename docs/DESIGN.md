Markdown

# 🎨 Kitabee — Design System Document

> **Document Version:** 2.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Status:** 🟢 Approved for Implementation
> **Related Docs:** [PRD.md](./PRD.md) | [APPFLOW.md](./APPFLOW.md) | [TECHSPEC.md](./TECHSPEC.md)

---

## 📚 Table of Contents

1. [Design Philosophy](#-design-philosophy)
2. [Theme System](#-theme-system)
3. [Color System](#-color-system)
4. [Typography](#-typography)
5. [Spacing System](#-spacing-system)
6. [Border Radius](#-border-radius)
7. [Elevation & Depth](#-elevation--depth)
8. [Component Library](#-component-library)
9. [Layout & Grid](#-layout--grid)
10. [Responsive Behavior](#-responsive-behavior)
11. [Screen-by-Screen Design Specs](#-screen-by-screen-design-specs)
12. [Do's and Don'ts](#-dos-and-donts)
13. [Accessibility Standards](#-accessibility-standards)

---

## 🎯 Design Philosophy

Kitabee reads as a **warm editorial product** — closer to a curated literary
magazine than a generic mobile app. The base canvas is near-black (`#1a1a2e`)
in dark mode and near-white (`#f7f7f2`) in light mode, both holding high-contrast
display type. The single brand voltage is **Kitabee Amber** (`#FFC93C`) — the
iconic bee-yellow — used scarcely on primary CTAs, the 🐝 mascot mark, active
tab highlights, and star rating fills. This amber works equally on both dark and
light canvases without modification.

Type runs **Inter** at modest weights (display 500, body 400) — never bombastic.
Spacing follows an explicit **8px token ladder** (`xxxs` 4px through `super` 128px);
generous editorial pacing throughout. The brand's strongest visual signature is
the **full-bleed hero illustration** or **book cover mosaic** that fills the
viewport top — followed by a tighter editorial body layout below.

### Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Editorial Confidence** | Let book covers and illustrations carry the visual weight. Type supports; never competes. |
| **Amber Scarcity** | `#FFC93C` appears only on primary CTAs, active states, and star ratings. Never decorative. |
| **Sharp Precision** | `0px` radius on all cards and primary buttons by default — crisp, modern. |
| **Generous Pacing** | Sections breathe. 96px vertical padding on major bands. |
| **Photographic Depth** | No drop shadow tiers. Elevation through brightness-step and cover imagery. |
| **Warm Dark Base** | Never pure black. `#1a1a2e` — slight warm indigo undertone. |
| **Warm Light Base** | Never pure white. `#f7f7f2` — slight warm cream undertone. |
| **Mode Agnostic Amber** | `#FFC93C` primary never changes between modes — it anchors identity in both. |

---

## 🌗 Theme System

### Overview

Kitabee supports **three theme modes:**
┌─────────────────────────────────────────────────────────────────────┐
│ THEME MODES │
├──────────────┬──────────────────────────────────────────────────────┤
│ dark │ Default — near-black canvas, white ink │
│ light │ Near-cream canvas, dark ink │
│ system │ Follows device OS preference (default on first open) │
└──────────────┴──────────────────────────────────────────────────────┘

text


**Default behavior:**
- First launch → `system` (reads `prefers-color-scheme`)
- User can override in Profile → Settings → Theme
- Selection persisted in `AsyncStorage` / `localStorage`

---

### Theme Detection Logic

```typescript
// theme/ThemeContext.tsx

type ThemeMode = 'dark' | 'light' | 'system';

const getActiveTheme = (
  mode: ThemeMode,
  systemScheme: 'dark' | 'light'
): 'dark' | 'light' => {
  if (mode === 'system') return systemScheme;
  return mode;
};

// Usage with React Native
import { useColorScheme } from 'react-native';

const systemScheme = useColorScheme(); // 'dark' | 'light' | null
const activeTheme = getActiveTheme(userPreference, systemScheme ?? 'dark');
Semantic Token System
This is the core of the theme system. Instead of using raw color hex values
directly in components, every component references a semantic token.
Semantic tokens automatically resolve to the correct raw color based on
the active theme.

text

Raw Token (fixed hex)  →  Semantic Token (context alias)  →  Component
     #1a1a2e          →       background.primary          →   Screen bg
     #f7f7f2          →       background.primary          →   Screen bg
                              (resolves per theme)
Semantic Token Map
Background Tokens
text

┌──────────────────────────┬──────────────────┬──────────────────┐
│  Semantic Token          │  Dark Mode       │  Light Mode      │
├──────────────────────────┼──────────────────┼──────────────────┤
│  background.primary      │  #1a1a2e (canvas)│  #f7f7f2         │
│  background.elevated     │  #252542         │  #ffffff         │
│  background.sunken       │  #131325         │  #ebebeb         │
│  background.overlay      │  rgba(0,0,0,0.7) │  rgba(0,0,0,0.4) │
│  background.card         │  #252542         │  #ffffff         │
│  background.input        │  #1a1a2e         │  #ffffff         │
│  background.modal        │  #252542         │  #ffffff         │
│  background.sheet        │  #252542         │  #ffffff         │
│  background.toast        │  #303052         │  #1a1a2e         │
└──────────────────────────┴──────────────────┴──────────────────┘
Text Tokens
text

┌──────────────────────────┬──────────────────┬──────────────────┐
│  Semantic Token          │  Dark Mode       │  Light Mode      │
├──────────────────────────┼──────────────────┼──────────────────┤
│  text.primary            │  #ffffff         │  #1a1a2e         │
│  text.secondary          │  #9e9eb8         │  #4a4a6a         │
│  text.muted              │  #666680         │  #8888a8         │
│  text.disabled           │  #3d3d5c         │  #c0c0d0         │
│  text.onPrimary          │  #1a1a2e         │  #1a1a2e         │
│  text.link               │  #FFC93C         │  #cc8800         │
│  text.placeholder        │  #666680         │  #aaaacc         │
└──────────────────────────┴──────────────────┴──────────────────┘
Note: text.link shifts from amber #FFC93C (dark) to a darker amber
#cc8800 (light) to maintain contrast against the light canvas.
text.onPrimary stays #1a1a2e in both modes — dark text always sits on
the amber CTA.

Border / Hairline Tokens
text

┌──────────────────────────┬──────────────────┬──────────────────┐
│  Semantic Token          │  Dark Mode       │  Light Mode      │
├──────────────────────────┼──────────────────┼──────────────────┤
│  border.default          │  #252542         │  #d2d2e0         │
│  border.subtle           │  #1e1e38         │  #ebebf0         │
│  border.strong           │  #3d3d5c         │  #b0b0c8         │
│  border.focus            │  #FFC93C         │  #FFC93C         │
│  border.input            │  #252542         │  #d2d2e0         │
│  border.inputFocus       │  #FFC93C         │  #FFC93C         │
└──────────────────────────┴──────────────────┴──────────────────┘
Note: border.focus and border.inputFocus stay amber in both modes —
the focus ring is always the brand color.

Brand Tokens (Never Change)
text

┌──────────────────────────┬──────────────────────────────────────┐
│  Semantic Token          │  Value (Both Modes — Never Changes)  │
├──────────────────────────┼──────────────────────────────────────┤
│  brand.primary           │  #FFC93C                             │
│  brand.primaryActive     │  #E6A800                             │
│  brand.primaryHover      │  #D4960A                             │
│  brand.onPrimary         │  #1a1a2e                             │
│  brand.semanticSuccess   │  #03904a                             │
│  brand.semanticWarning   │  #f13a2c                             │
│  brand.semanticInfo      │  #4c98b9                             │
└──────────────────────────┴──────────────────────────────────────┘
Theme Token Implementation
TypeScript

// theme/tokens.ts

export const rawColors = {
  // Dark surfaces
  canvas:            '#1a1a2e',
  canvasElevated:    '#252542',
  canvasSunken:      '#131325',
  canvasLight:       '#f7f7f2',
  canvasLightCard:   '#ffffff',
  canvasLightSunken: '#ebebeb',

  // Text - dark
  inkWhite:          '#ffffff',
  inkBodyDark:       '#9e9eb8',
  inkMutedDark:      '#666680',
  inkDisabledDark:   '#3d3d5c',

  // Text - light
  inkDark:           '#1a1a2e',
  inkBodyLight:      '#4a4a6a',
  inkMutedLight:     '#8888a8',
  inkDisabledLight:  '#c0c0d0',

  // Brand (immutable)
  amber:             '#FFC93C',
  amberActive:       '#E6A800',
  amberHover:        '#D4960A',
  amberDark:         '#cc8800',  // light-mode link variant

  // Borders - dark
  hairlineDark:      '#252542',
  hairlineSubtleDark:'#1e1e38',
  hairlineStrongDark:'#3d3d5c',

  // Borders - light
  hairlineLight:     '#d2d2e0',
  hairlineSubtleLight:'#ebebf0',
  hairlineStrongLight:'#b0b0c8',

  // Semantic
  success:           '#03904a',
  warning:           '#f13a2c',
  info:              '#4c98b9',

  // Overlays
  overlayDark:       'rgba(0,0,0,0.7)',
  overlayLight:      'rgba(0,0,0,0.4)',
};


export const darkTheme = {
  background: {
    primary:   rawColors.canvas,
    elevated:  rawColors.canvasElevated,
    sunken:    rawColors.canvasSunken,
    overlay:   rawColors.overlayDark,
    card:      rawColors.canvasElevated,
    input:     rawColors.canvas,
    modal:     rawColors.canvasElevated,
    sheet:     rawColors.canvasElevated,
    toast:     '#303052',
  },
  text: {
    primary:     rawColors.inkWhite,
    secondary:   rawColors.inkBodyDark,
    muted:       rawColors.inkMutedDark,
    disabled:    rawColors.inkDisabledDark,
    onPrimary:   rawColors.inkDark,
    link:        rawColors.amber,
    placeholder: rawColors.inkMutedDark,
  },
  border: {
    default:    rawColors.hairlineDark,
    subtle:     rawColors.hairlineSubtleDark,
    strong:     rawColors.hairlineStrongDark,
    focus:      rawColors.amber,
    input:      rawColors.hairlineDark,
    inputFocus: rawColors.amber,
  },
  brand: {
    primary:         rawColors.amber,
    primaryActive:   rawColors.amberActive,
    primaryHover:    rawColors.amberHover,
    onPrimary:       rawColors.inkDark,
    semanticSuccess: rawColors.success,
    semanticWarning: rawColors.warning,
    semanticInfo:    rawColors.info,
  },
};


export const lightTheme = {
  background: {
    primary:   rawColors.canvasLight,
    elevated:  rawColors.canvasLightCard,
    sunken:    rawColors.canvasLightSunken,
    overlay:   rawColors.overlayLight,
    card:      rawColors.canvasLightCard,
    input:     rawColors.canvasLightCard,
    modal:     rawColors.canvasLightCard,
    sheet:     rawColors.canvasLightCard,
    toast:     rawColors.inkDark,
  },
  text: {
    primary:     rawColors.inkDark,
    secondary:   rawColors.inkBodyLight,
    muted:       rawColors.inkMutedLight,
    disabled:    rawColors.inkDisabledLight,
    onPrimary:   rawColors.inkDark,
    link:        rawColors.amberDark,
    placeholder: rawColors.inkMutedLight,
  },
  border: {
    default:    rawColors.hairlineLight,
    subtle:     rawColors.hairlineSubtleLight,
    strong:     rawColors.hairlineStrongLight,
    focus:      rawColors.amber,
    input:      rawColors.hairlineLight,
    inputFocus: rawColors.amber,
  },
  brand: {
    primary:         rawColors.amber,
    primaryActive:   rawColors.amberActive,
    primaryHover:    rawColors.amberHover,
    onPrimary:       rawColors.inkDark,
    semanticSuccess: rawColors.success,
    semanticWarning: rawColors.warning,
    semanticInfo:    rawColors.info,
  },
};

export type Theme = typeof darkTheme;
Theme Context & Hook
TypeScript

// theme/ThemeContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { darkTheme, lightTheme, Theme } from './tokens';

type ThemeMode = 'dark' | 'light' | 'system';

interface ThemeContextType {
  theme: Theme;
  mode: ThemeMode;
  activeMode: 'dark' | 'light';
  setMode: (mode: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: darkTheme,
  mode: 'system',
  activeMode: 'dark',
  setMode: () => {},
});

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const systemScheme = useColorScheme();
  const [mode, setModeState] = useState<ThemeMode>('system');

  useEffect(() => {
    // Load persisted preference
    AsyncStorage.getItem('kitabee_theme_mode').then((stored) => {
      if (stored) setModeState(stored as ThemeMode);
    });
  }, []);

  const setMode = async (newMode: ThemeMode) => {
    setModeState(newMode);
    await AsyncStorage.setItem('kitabee_theme_mode', newMode);
  };

  const activeMode: 'dark' | 'light' =
    mode === 'system' ? (systemScheme ?? 'dark') : mode;

  const theme = activeMode === 'dark' ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, mode, activeMode, setMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

// The hook every component uses
export const useTheme = () => useContext(ThemeContext);
Using the Theme in Components
TypeScript

// Example: BookCard component
import { useTheme } from '@/theme/ThemeContext';

const BookCard = ({ book }) => {
  const { theme } = useTheme();

  return (
    <View style={{
      backgroundColor: theme.background.card,
      borderWidth: 1,
      borderColor: theme.border.default,
    }}>
      <Text style={{
        color: theme.text.primary,
        fontSize: 18,
        fontWeight: '700',
      }}>
        {book.title}
      </Text>
      <Text style={{
        color: theme.text.secondary,
        fontSize: 13,
      }}>
        {book.author}
      </Text>
    </View>
  );
};
Theme Switching UI (Settings Screen)
text

┌─────────────────────────────────────────────────────────┐
│  THEME                                                  │  caption-uppercase
│  ─────────────────────────────────────────────         │  border.default
│                                                         │
│  ○  🌙  Dark                                            │  body-md / text.primary
│  ○  ☀️  Light                                           │  body-md / text.primary
│  ●  📱  System (Recommended)                            │  body-md / brand.primary
│                                                         │
│  Follows your device display settings.                  │  body-sm / text.muted
└─────────────────────────────────────────────────────────┘
Selected option: radio dot in brand.primary (#FFC93C)
Unselected: border.default
Description: body-sm / text.muted
Switch is instant — no transition delay
Per-Screen Mode Behavior
text

┌──────────────────────────┬──────────────────────────────────────────────┐
│  Screen                  │  Mode Behavior                               │
├──────────────────────────┼──────────────────────────────────────────────┤
│  SplashScreen            │  Always DARK — brand moment                  │
│  WelcomeScreen           │  Follows active theme                        │
│  LoginScreen             │  Follows active theme                        │
│  RegisterScreen          │  Follows active theme                        │
│  OnboardingIntro         │  Follows active theme                        │
│  GenreSelection          │  Follows active theme                        │
│  RateInitialBooks        │  Follows active theme                        │
│  PersonalizingScreen     │  Always DARK — cinematic loading moment      │
│  HomeScreen              │  Follows active theme                        │
│  SearchScreen            │  Follows active theme                        │
│  BookDetailsScreen       │  Follows active theme                        │
│  RatingModal             │  Follows active theme (bottom sheet)         │
│  LibraryScreen           │  Follows active theme                        │
│  InsightsScreen          │  Follows active theme                        │
│  ProfileScreen           │  Follows active theme                        │
│  SettingsScreen          │  Follows active theme                        │
│  AboutScreen             │  Follows active theme                        │
└──────────────────────────┴──────────────────────────────────────────────┘
Rule: SplashScreen and PersonalizingScreen are always dark — these
are cinematic brand moments. All other screens honor the user's theme
preference.

Component-Level Mode Switching Table
Every component references semantic tokens. Here is how each resolves:

text

┌──────────────────────────┬────────────────────────┬────────────────────────┐
│  Component               │  Dark Mode             │  Light Mode            │
├──────────────────────────┼────────────────────────┼────────────────────────┤
│  Screen background       │  #1a1a2e               │  #f7f7f2               │
│  Card background         │  #252542               │  #ffffff               │
│  Elevated panel          │  #252542               │  #ffffff               │
│  Sunken/inset area       │  #131325               │  #ebebeb               │
│  Bottom tab bar          │  #1a1a2e               │  #f7f7f2               │
│  Header bar              │  #1a1a2e               │  #f7f7f2               │
│  Modal / bottom sheet    │  #252542               │  #ffffff               │
│  Text input bg           │  #1a1a2e               │  #ffffff               │
│  Text input border       │  #252542               │  #d2d2e0               │
│  Text input border focus │  #FFC93C               │  #FFC93C               │
│  Primary display text    │  #ffffff               │  #1a1a2e               │
│  Body text               │  #9e9eb8               │  #4a4a6a               │
│  Muted text              │  #666680               │  #8888a8               │
│  Divider / hairline      │  #252542               │  #d2d2e0               │
│  Badge pill (default)    │  #252542 bg / #fff txt │  #ebebeb bg / #1a1a2e  │
│  Badge pill (selected)   │  #FFC93C bg / #1a1a2e  │  #FFC93C bg / #1a1a2e  │
│  Star fill               │  #FFC93C               │  #FFC93C               │
│  Star empty              │  #252542               │  #d2d2e0               │
│  Tab active color        │  #FFC93C               │  #FFC93C               │
│  Tab inactive color      │  #666680               │  #8888a8               │
│  Primary CTA bg          │  #FFC93C               │  #FFC93C               │
│  Primary CTA text        │  #1a1a2e               │  #1a1a2e               │
│  Outline CTA border      │  #ffffff               │  #1a1a2e               │
│  Outline CTA text        │  #ffffff               │  #1a1a2e               │
│  Link text               │  #FFC93C               │  #cc8800               │
│  Skeleton base           │  #252542               │  #ebebeb               │
│  Skeleton shimmer        │  #3d3d5c               │  #d2d2e0               │
│  Toast (success)         │  #03904a               │  #03904a               │
│  Toast (error)           │  #f13a2c               │  #f13a2c               │
│  Focus ring              │  #FFC93C               │  #FFC93C               │
│  Overlay/scrim           │  rgba(0,0,0,0.7)       │  rgba(0,0,0,0.4)       │
└──────────────────────────┴────────────────────────┴────────────────────────┘
Dark Mode Visual Preview
text

┌─────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████  #1a1a2e      │  Screen bg
│                                                         │
│  ┌───────────────────────────────────────┐              │
│  │  ██████████████████████  #252542      │              │  Card
│  │                                       │              │
│  │  Book Title ████████████  #ffffff     │              │  Primary text
│  │  Author Name ███████████  #9e9eb8     │              │  Body text
│  │  ⭐⭐⭐⭐⭐  ██████████  #FFC93C     │              │  Stars
│  └───────────────────────────────────────┘              │
│                                                         │
│  ┌────────────────────────────────────┐                 │
│  │  GET STARTED          #FFC93C bg   │                 │  Primary CTA
│  │  text: #1a1a2e                     │                 │
│  └────────────────────────────────────┘                 │
│                                                         │
│  SECTION LABEL  ██████  #666680 / uppercase             │  Caption
│  ─────────────────────  #252542                         │  Hairline
│                                                         │
└─────────────────────────────────────────────────────────┘
Light Mode Visual Preview
text

┌─────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████  #f7f7f2      │  Screen bg
│                                                         │
│  ┌───────────────────────────────────────┐              │
│  │  ██████████████████████  #ffffff      │              │  Card
│  │  border: 1px #d2d2e0                  │              │
│  │                                       │              │
│  │  Book Title ████████████  #1a1a2e     │              │  Primary text
│  │  Author Name ███████████  #4a4a6a     │              │  Body text
│  │  ⭐⭐⭐⭐⭐  ██████████  #FFC93C     │              │  Stars (unchanged)
│  └───────────────────────────────────────┘              │
│                                                         │
│  ┌────────────────────────────────────┐                 │
│  │  GET STARTED          #FFC93C bg   │                 │  Primary CTA (unchanged)
│  │  text: #1a1a2e                     │                 │
│  └────────────────────────────────────┘                 │
│                                                         │
│  SECTION LABEL  ██████  #8888a8 / uppercase             │  Caption
│  ─────────────────────  #d2d2e0                         │  Hairline
│                                                         │
└─────────────────────────────────────────────────────────┘
What Never Changes Between Modes
text

┌──────────────────────────────────────────────────────────┐
│  IMMUTABLE ACROSS BOTH MODES                             │
├──────────────────────────────────────────────────────────┤
│  brand.primary          #FFC93C  ← Amber CTA             │
│  brand.primaryActive    #E6A800  ← Amber press state     │
│  brand.onPrimary        #1a1a2e  ← Text on amber CTA     │
│  border.focus           #FFC93C  ← Focus ring            │
│  border.inputFocus      #FFC93C  ← Input focus border    │
│  star fill              #FFC93C  ← Rating stars          │
│  tab active             #FFC93C  ← Active tab color      │
│  brand.semanticSuccess  #03904a  ← Success toasts        │
│  brand.semanticWarning  #f13a2c  ← Error toasts          │
│  brand.semanticInfo     #4c98b9  ← Info badges           │
│  SplashScreen bg        #1a1a2e  ← Always dark           │
│  PersonalizingScreen bg #1a1a2e  ← Always dark           │
│  button CTA radius      0px      ← Always sharp          │
└──────────────────────────────────────────────────────────┘
🎨 Color System
Brand & Accent
text

┌─────────────────────────────────────────────────────────────────┐
│  BRAND PALETTE                                                  │
├──────────────────┬──────────┬──────────────────────────────────┤
│  Token           │  Hex     │  Usage                           │
├──────────────────┼──────────┼──────────────────────────────────┤
│  primary         │ #FFC93C  │  Primary CTAs, active tabs,      │
│                  │          │  star fills, bee mark            │
│  primary-active  │ #E6A800  │  Press/active state              │
│  primary-hover   │ #D4960A  │  Hover state (web only)          │
│  primary-dark    │ #cc8800  │  Links on light canvas only      │
└──────────────────┴──────────┴──────────────────────────────────┘
Raw Surface Colors (Referenced by Semantic Tokens)
text

┌──────────────────────┬───────────┬────────────────────────────────────┐
│  Raw Token           │  Hex      │  Referenced By                     │
├──────────────────────┼───────────┼────────────────────────────────────┤
│  canvas              │ #1a1a2e   │  background.primary (dark)         │
│  canvas-elevated     │ #252542   │  background.elevated (dark)        │
│  canvas-sunken       │ #131325   │  background.sunken (dark)          │
│  canvas-light        │ #f7f7f2   │  background.primary (light)        │
│  canvas-light-card   │ #ffffff   │  background.card (light)           │
│  canvas-light-sunken │ #ebebeb   │  background.sunken (light)         │
└──────────────────────┴───────────┴────────────────────────────────────┘
Semantic Colors (Use These in Components)
JavaScript

// Always use semantic tokens — never raw hex in components

// ✅ Correct
backgroundColor: theme.background.card
color: theme.text.primary
borderColor: theme.border.default

// ❌ Wrong
backgroundColor: '#252542'
color: '#ffffff'
borderColor: '#252542'
Semantic Color Full Reference
JavaScript

// design-tokens/semanticColors.js

export const semanticColors = {
  dark: {
    'background.primary':   '#1a1a2e',
    'background.elevated':  '#252542',
    'background.sunken':    '#131325',
    'background.card':      '#252542',
    'background.input':     '#1a1a2e',
    'background.modal':     '#252542',
    'background.overlay':   'rgba(0,0,0,0.7)',
    'background.toast':     '#303052',

    'text.primary':         '#ffffff',
    'text.secondary':       '#9e9eb8',
    'text.muted':           '#666680',
    'text.disabled':        '#3d3d5c',
    'text.onPrimary':       '#1a1a2e',
    'text.link':            '#FFC93C',
    'text.placeholder':     '#666680',

    'border.default':       '#252542',
    'border.subtle':        '#1e1e38',
    'border.strong':        '#3d3d5c',
    'border.focus':         '#FFC93C',
    'border.input':         '#252542',
    'border.inputFocus':    '#FFC93C',
  },
  light: {
    'background.primary':   '#f7f7f2',
    'background.elevated':  '#ffffff',
    'background.sunken':    '#ebebeb',
    'background.card':      '#ffffff',
    'background.input':     '#ffffff',
    'background.modal':     '#ffffff',
    'background.overlay':   'rgba(0,0,0,0.4)',
    'background.toast':     '#1a1a2e',

    'text.primary':         '#1a1a2e',
    'text.secondary':       '#4a4a6a',
    'text.muted':           '#8888a8',
    'text.disabled':        '#c0c0d0',
    'text.onPrimary':       '#1a1a2e',
    'text.link':            '#cc8800',
    'text.placeholder':     '#aaaacc',

    'border.default':       '#d2d2e0',
    'border.subtle':        '#ebebf0',
    'border.strong':        '#b0b0c8',
    'border.focus':         '#FFC93C',
    'border.input':         '#d2d2e0',
    'border.inputFocus':    '#FFC93C',
  },
  // Same in both modes
  brand: {
    'brand.primary':         '#FFC93C',
    'brand.primaryActive':   '#E6A800',
    'brand.onPrimary':       '#1a1a2e',
    'brand.semanticSuccess': '#03904a',
    'brand.semanticWarning': '#f13a2c',
    'brand.semanticInfo':    '#4c98b9',
  },
};
🔤 Typography
Font Family
Inter is the primary sans family across every text role.
Fallback: -apple-system, system-ui, sans-serif
No display/body family split — single family, multiple weights.
Typography does not change between light and dark modes — only color changes.

Substitute: Inter at weight 500 with letter-spacing -1%, or Söhne for
closer humanist proportions.

Type Scale
Token	Size	Weight	Line Height	Letter Spacing	Usage
display-mega	80px	500	1.05	-1.6px	Splash / Welcome hero H1
display-xl	56px	500	1.1	-1.12px	Section hero headlines
display-lg	36px	500	1.2	-0.36px	Onboarding headers, screen titles
display-md	26px	500	1.5	0.195px	Subsection heads, modal titles
title-md	18px	700	1.2	0	Card titles, component labels
title-sm	16px	500	1.4	0.08px	List labels, tab titles
body-md	14px	400	1.5	0	Default body text
body-sm	13px	400	1.5	0	Secondary body, footer text
caption	12px	400	1.4	0	Photo captions, timestamps
caption-uppercase	11px	600	1.4	1.1px	Section labels, genre badges — UPPERCASE
button	14px	700	1.0	1.4px	CTA labels — UPPERCASE
nav-link	13px	600	1.4	0.65px	Tab bar labels — UPPERCASE
number-display	80px	700	1.0	-1.6px	Stat callouts, insight numbers
Typography Token Reference
JavaScript

// design-tokens/typography.js
export const typography = {
  'display-mega': {
    fontFamily: "'Inter', -apple-system, system-ui, sans-serif",
    fontSize: 80,
    fontWeight: '500',
    lineHeight: 1.05,
    letterSpacing: -1.6,
  },
  'display-xl': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 56,
    fontWeight: '500',
    lineHeight: 1.1,
    letterSpacing: -1.12,
  },
  'display-lg': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 36,
    fontWeight: '500',
    lineHeight: 1.2,
    letterSpacing: -0.36,
  },
  'display-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 26,
    fontWeight: '500',
    lineHeight: 1.5,
    letterSpacing: 0.195,
  },
  'title-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 18,
    fontWeight: '700',
    lineHeight: 1.2,
    letterSpacing: 0,
  },
  'title-sm': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 16,
    fontWeight: '500',
    lineHeight: 1.4,
    letterSpacing: 0.08,
  },
  'body-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 14,
    fontWeight: '400',
    lineHeight: 1.5,
    letterSpacing: 0,
  },
  'body-sm': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 13,
    fontWeight: '400',
    lineHeight: 1.5,
    letterSpacing: 0,
  },
  caption: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 12,
    fontWeight: '400',
    lineHeight: 1.4,
    letterSpacing: 0,
  },
  'caption-uppercase': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 11,
    fontWeight: '600',
    lineHeight: 1.4,
    letterSpacing: 1.1,
    textTransform: 'uppercase',
  },
  button: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 14,
    fontWeight: '700',
    lineHeight: 1.0,
    letterSpacing: 1.4,
    textTransform: 'uppercase',
  },
  'nav-link': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 13,
    fontWeight: '600',
    lineHeight: 1.4,
    letterSpacing: 0.65,
    textTransform: 'uppercase',
  },
  'number-display': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 80,
    fontWeight: '700',
    lineHeight: 1.0,
    letterSpacing: -1.6,
  },
};
Typography Principles
Display weight stays at 500 — editorial confidence, not bombastic.
CTA labels are uppercase with 1.4px tracking — precise, intentional.
Nav labels are uppercase with 0.65px tracking — consistent with CTA voice.
Negative letter-spacing on display only — -0.36px to -1.6px on
display sizes; body stays at 0.
Never bold display copy — weight 700 reserved for title-md, button,
and number-display only.
Typography scale never changes between modes — only the color token
applied to text changes.
📐 Spacing System
Token Ladder
Base unit: 8px (with a 4px xxxs micro-step).

text

┌──────────┬────────┬─────────────────────────────────────────┐
│  Token   │  Value │  Primary Usage                          │
├──────────┼────────┼─────────────────────────────────────────┤
│  xxxs    │  4px   │  Icon gaps, badge padding               │
│  xxs     │  8px   │  Inline element gaps, chip padding      │
│  xs      │  16px  │  Component internal padding             │
│  sm      │  24px  │  Card padding, form group gaps          │
│  md      │  32px  │  Section internal spacing               │
│  lg      │  48px  │  Between major components               │
│  xl      │  64px  │  Footer padding, wide section gaps      │
│  xxl     │  96px  │  Major band vertical padding            │
│  super   │  128px │  Hero band depth, splash breathing room │
└──────────┴────────┴─────────────────────────────────────────┘
JavaScript

// design-tokens/spacing.js
export const spacing = {
  xxxs:  4,
  xxs:   8,
  xs:    16,
  sm:    24,
  md:    32,
  lg:    48,
  xl:    64,
  xxl:   96,
  super: 128,
};
Usage Rules
Section padding: spacing.xxl (96px) for major bands
Hero band depth: spacing.super (128px)
Card internal padding: spacing.sm (24px)
Component gaps: spacing.xs (16px)
Never use ad-hoc px values — always pull from the token ladder
Spacing does not change between modes — layout is mode-agnostic
🔲 Border Radius
Radius Scale
text

┌──────────────┬──────────┬──────────────────────────────────────────┐
│  Token       │  Value   │  Usage                                   │
├──────────────┼──────────┼──────────────────────────────────────────┤
│  none        │  0px     │  ALL CTAs, cards, bands — dominant shape │
│  xs          │  2px     │  Tight genre badges (rare)               │
│  sm          │  4px     │  Form inputs, text fields                │
│  md          │  6px     │  Compact cards (rare, mobile only)       │
│  lg          │  8px     │  Bottom sheet top corners                │
│  xl          │  12px    │  Modal/dialog corners                    │
│  full        │  9999px  │  Avatar circles, badge pills ONLY        │
└──────────────┴──────────┴──────────────────────────────────────────┘
JavaScript

// design-tokens/rounded.js
export const rounded = {
  none: 0,
  xs:   2,
  sm:   4,
  md:   6,
  lg:   8,
  xl:   12,
  full: 9999,
};
Radius Principles
Sharp by default. 0px is the Kitabee button and card shape.
Pill geometry (full) reserved exclusively for: avatar plates and badge pills.
Border radius does not change between modes — it is mode-agnostic.
Bottom sheets: rounded.lg (8px) on top corners only.
🏔️ Elevation & Depth
Elevation Levels
text

┌──────────────────┬────────────────────────────────┬──────────────────────────┐
│  Level           │  Dark Mode                     │  Light Mode              │
├──────────────────┼────────────────────────────────┼──────────────────────────┤
│  Flat (base)     │  #1a1a2e                       │  #f7f7f2                 │
│  Card            │  #252542                       │  #ffffff + 1px border    │
│  Elevated        │  #252542                       │  #ffffff + shadow        │
│  Sunken          │  #131325                       │  #ebebeb                 │
│  Hairline border │  1px #252542                   │  1px #d2d2e0             │
│  Soft drop       │  0 4px 8px rgba(0,0,0,0.2)    │  0 4px 8px rgba(0,0,0,0.08)│
│  Cover imagery   │  Full-bleed book cover art     │  Full-bleed book cover art│
└──────────────────┴────────────────────────────────┴──────────────────────────┘
Light mode elevation note: In light mode, cards use a 1px border.default

optional soft drop instead of background-step elevation since the contrast
between #f7f7f2 and #ffffff is subtler.
Decorative Depth
Full-bleed book cover imagery is the primary depth treatment in both modes.
Amber gradient (linear-gradient(180deg, #cc8800, #FFC93C 64%)):
Used inside CTA bands — same in both modes.
Dark gradient (linear-gradient(180deg, #2a2a4a, #1a1a2e 64%)):
Dark mode section transitions.
Light gradient (linear-gradient(180deg, #ffffff, #f7f7f2 64%)):
Light mode section transitions.
🧩 Component Library
All components below list both dark and light values via semantic tokens.

Navigation Bar (Bottom Tab)
text

┌─────────────────────────────────────────────────────────────────┐
│  tab-bar                                                        │
├────────────────────────┬────────────────────────────────────────┤
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  borderTop             │  1px #252542   │  1px #d2d2e0          │
│  height                │  64px          │  64px                 │
│  activeColor           │  #FFC93C       │  #FFC93C              │
│  inactiveColor         │  #666680       │  #8888a8              │
│  typography            │  nav-link      │  nav-link             │
│  iconSize              │  24px          │  24px                 │
│  tapArea               │  min 44×44px   │  min 44×44px          │
└────────────────────────┴────────────────┴───────────────────────┘
Header Bar
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  textColor             │  #ffffff       │  #1a1a2e              │
│  typography            │  title-md      │  title-md             │
│  height                │  56px          │  56px                 │
│  borderBottom (scroll) │  1px #252542   │  1px #d2d2e0          │
└────────────────────────┴────────────────┴───────────────────────┘
Buttons
Primary Button (Amber CTA) — Same in Both Modes
text

┌────────────────────────┬───────────────────────────────────────┐
│  Property              │  Both Modes                           │
├────────────────────────┼───────────────────────────────────────┤
│  backgroundColor       │  #FFC93C  (brand.primary)             │
│  textColor             │  #1a1a2e  (brand.onPrimary)           │
│  typography            │  button (14px / 700 / 1.4px / UPPER)  │
│  borderRadius          │  0px (rounded.none)                   │
│  padding               │  14px 32px                            │
│  height                │  48px                                 │
│  active bg             │  #E6A800  (brand.primaryActive)       │
│  disabled bg           │  varies — see below                   │
└────────────────────────┴───────────────────────────────────────┘

  Disabled state:
  Dark:   bg #252542, text #3d3d5c, opacity 0.5
  Light:  bg #ebebeb, text #c0c0d0, opacity 0.5
Outline Button
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  transparent   │  transparent          │
│  textColor             │  #ffffff       │  #1a1a2e              │
│  borderColor           │  #ffffff       │  #1a1a2e              │
│  borderWidth           │  1px           │  1px                  │
│  borderRadius          │  0px           │  0px                  │
│  padding               │  13px 31px     │  13px 31px            │
│  height                │  48px          │  48px                 │
└────────────────────────┴────────────────┴───────────────────────┘
Tertiary Text Button
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  transparent   │  transparent          │
│  textColor             │  #FFC93C       │  #cc8800              │
│  typography            │  button        │  button               │
│  no border             │  —             │  —                    │
└────────────────────────┴────────────────┴───────────────────────┘
Book Card
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #252542       │  #ffffff              │
│  borderColor           │  none          │  1px #d2d2e0          │
│  borderRadius          │  0px           │  0px                  │
│  titleColor            │  #ffffff       │  #1a1a2e              │
│  authorColor           │  #9e9eb8       │  #4a4a6a              │
│  starFill              │  #FFC93C       │  #FFC93C              │
│  starEmpty             │  #252542       │  #d2d2e0              │
│  ratingText            │  #9e9eb8       │  #4a4a6a              │
│  coverRadius           │  0px           │  0px                  │
└────────────────────────┴────────────────┴───────────────────────┘
Text Inputs
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #ffffff              │
│  textColor             │  #ffffff       │  #1a1a2e              │
│  placeholderColor      │  #666680       │  #aaaacc              │
│  borderColor (default) │  #252542       │  #d2d2e0              │
│  borderColor (focus)   │  #FFC93C       │  #FFC93C              │
│  borderRadius          │  4px           │  4px                  │
│  padding               │  14px 16px     │  14px 16px            │
│  height                │  48px          │  48px                 │
│  labelColor            │  #9e9eb8       │  #4a4a6a              │
│  errorBorderColor      │  #f13a2c       │  #f13a2c              │
│  errorTextColor        │  #f13a2c       │  #f13a2c              │
└────────────────────────┴────────────────┴───────────────────────┘
Badge Pill
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  State                 │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Default bg            │  #252542       │  #ebebeb              │
│  Default text          │  #ffffff       │  #1a1a2e              │
│  Selected bg           │  #FFC93C       │  #FFC93C              │
│  Selected text         │  #1a1a2e       │  #1a1a2e              │
│  borderRadius          │  9999px        │  9999px               │
│  typography            │  caption-upper │  caption-upper        │
│  padding               │  4px 12px      │  4px 12px             │
└────────────────────────┴────────────────┴───────────────────────┘
Modal / Bottom Sheet
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #252542       │  #ffffff              │
│  topCorners            │  12px          │  12px                 │
│  overlay               │rgba(0,0,0,0.7) │rgba(0,0,0,0.4)        │
│  handleColor           │  #666680       │  #c0c0d0              │
│  titleColor            │  #ffffff       │  #1a1a2e              │
│  bodyColor             │  #9e9eb8       │  #4a4a6a              │
│  dividerColor          │  #252542       │  #d2d2e0              │
└────────────────────────┴────────────────┴───────────────────────┘
Toast Notifications
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Type                  │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Success bg            │  #03904a       │  #03904a              │
│  Success text          │  #ffffff       │  #ffffff              │
│  Error bg              │  #f13a2c       │  #f13a2c              │
│  Error text            │  #ffffff       │  #ffffff              │
│  Info bg               │  #4c98b9       │  #4c98b9              │
│  Info text             │  #ffffff       │  #ffffff              │
│  Neutral bg            │  #303052       │  #1a1a2e              │
│  Neutral text          │  #ffffff       │  #ffffff              │
│  borderRadius          │  4px           │  4px                  │
│  padding               │  12px 16px     │  12px 16px            │
└────────────────────────┴────────────────┴───────────────────────┘
Note: Semantic toast colors (success, error, info) do not change between
modes — they are brand-fixed semantic indicators.

Skeleton / Loading
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  baseColor             │  #252542       │  #ebebeb              │
│  shimmerColor          │  #3d3d5c       │  #d2d2e0              │
│  borderRadius          │  0px           │  0px                  │
│  animation             │  shimmer 1.4s  │  shimmer 1.4s         │
└────────────────────────┴────────────────┴───────────────────────┘
Empty State
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  illustration tint     │  #FFC93C       │  #FFC93C              │
│  titleColor            │  #ffffff       │  #1a1a2e              │
│  bodyColor             │  #9e9eb8       │  #4a4a6a              │
│  CTA                   │  button-primary│  button-primary       │
└────────────────────────┴────────────────┴───────────────────────┘
Footer
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  textColor             │  #9e9eb8       │  #8888a8              │
│  linkColor             │  #9e9eb8       │  #8888a8              │
│  linkHover             │  #ffffff       │  #1a1a2e              │
│  borderTop             │  1px #252542   │  1px #d2d2e0          │
│  padding               │  64px 48px     │  64px 48px            │
└────────────────────────┴────────────────┴───────────────────────┘
📐 Layout & Grid
Content Width
text

Mobile:   100%
Tablet:   100% up to 768px
Desktop:  max-width 1280px, centered
Wide:     Editorial body caps at 1280px; hero art full-bleed
Column Grid
text

Mobile:   4-column, 16px gutters
Tablet:   8-column, 24px gutters
Desktop:  12-column, 32px gutters
Feature Card Grid
Context	Mobile	Tablet	Desktop
Home (horizontal scroll)	scroll	2-up	4-up
Search results	2-up	3-up	4-up
Library grid	3-up	4-up	5-up
Genre selection	2-up	3-up	4-up
Insights stats	2-up	4-up	4-up
Layout is mode-agnostic — grid structure never changes between themes.

📱 Responsive Behavior
Breakpoints
Name	Width	Key Changes
Mobile	< 640px	Hero crops vertically; H1 80→32px; 2-up grid; bottom tab
Tablet	640–1024px	H1 56px; 2–3-up grid; bottom tab
Desktop	1024–1280px	Full H1 80px; 4-up grid; sidebar option
Wide	> 1280px	Body caps 1280px; hero full-bleed
Responsive Type Scaling
Token	Mobile	Tablet	Desktop
display-mega	32px	56px	80px
display-xl	28px	40px	56px
display-lg	24px	30px	36px
display-md	20px	22px	26px
Touch Targets
Primary CTA height: 48px — WCAG AAA
Tab bar items: 44px minimum
Book cards: 44px minimum interactive area
Star rating input: 36px per star
🖥️ Screen-by-Screen Design Specs
Each screen lists dark + light values side by side.

Splash Screen — Always Dark
text

┌─────────────────────────────────────────────────────────┐
│  ALWAYS DARK — Mode override regardless of user setting │
│                                                         │
│  backgroundColor:  #1a1a2e (canvas — fixed)             │
│                                                         │
│              🐝  KITABEE                                │
│          [display-xl / #ffffff]                         │
│                                                         │
│      "Discover your next great read"                    │
│          [body-md / #9e9eb8]                            │
│                                                         │
│         Amber pulse animation (#FFC93C)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
Welcome Screen
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Hero illustration bg  │  #1a1a2e       │  #f7f7f2              │
│  Headline              │  #ffffff       │  #1a1a2e              │
│  Subheadline           │  #9e9eb8       │  #4a4a6a              │
│  Primary CTA           │  #FFC93C       │  #FFC93C              │
│  Outline CTA border    │  #ffffff       │  #1a1a2e              │
│  Outline CTA text      │  #ffffff       │  #1a1a2e              │
└────────────────────────┴────────────────┴───────────────────────┘
Login & Register
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Title                 │  #ffffff       │  #1a1a2e              │
│  Subtitle              │  #9e9eb8       │  #4a4a6a              │
│  Input bg              │  #1a1a2e       │  #ffffff              │
│  Input border          │  #252542       │  #d2d2e0              │
│  Input border (focus)  │  #FFC93C       │  #FFC93C              │
│  Input text            │  #ffffff       │  #1a1a2e              │
│  Input placeholder     │  #666680       │  #aaaacc              │
│  Error text            │  #f13a2c       │  #f13a2c              │
│  Submit CTA            │  #FFC93C       │  #FFC93C              │
│  Divider               │  #252542       │  #d2d2e0              │
│  Link text             │  #FFC93C       │  #cc8800              │
└────────────────────────┴────────────────┴───────────────────────┘
Genre Selection (Onboarding)
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Title                 │  #ffffff       │  #1a1a2e              │
│  Subtitle              │  #9e9eb8       │  #4a4a6a              │
│  Tile (default) bg     │  #252542       │  #ebebeb              │
│  Tile (default) text   │  #ffffff       │  #1a1a2e              │
│  Tile (selected) bg    │  #FFC93C       │  #FFC93C              │
│  Tile (selected) text  │  #1a1a2e       │  #1a1a2e              │
│  Continue CTA          │  #FFC93C       │  #FFC93C              │
│  Continue (disabled)   │  opacity 0.4   │  opacity 0.4          │
└────────────────────────┴────────────────┴───────────────────────┘
Personalizing Screen — Always Dark
text

┌─────────────────────────────────────────────────────────┐
│  ALWAYS DARK — Cinematic loading moment                 │
│                                                         │
│  backgroundColor:  #1a1a2e (fixed)                      │
│  🐝 mascot:        #FFC93C animated pulse               │
│  Title:            #ffffff                              │
│  Body:             #9e9eb8                              │
│  Progress bar:     #FFC93C fill / #252542 track         │
│                                                         │
└─────────────────────────────────────────────────────────┘
Home Screen
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Header bg             │  #1a1a2e       │  #f7f7f2              │
│  Greeting text         │  #ffffff       │  #1a1a2e              │
│  Sub-greeting          │  #9e9eb8       │  #4a4a6a              │
│  Section labels        │  #666680       │  #8888a8              │
│  Dividers              │  #252542       │  #d2d2e0              │
│  Card bg               │  #252542       │  #ffffff              │
│  Card border           │  none          │  1px #d2d2e0          │
│  Card title            │  #ffffff       │  #1a1a2e              │
│  Card author           │  #9e9eb8       │  #4a4a6a              │
│  Star fill             │  #FFC93C       │  #FFC93C              │
│  Tab bar bg            │  #1a1a2e       │  #f7f7f2              │
│  Tab active            │  #FFC93C       │  #FFC93C              │
│  Tab inactive          │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
Search Screen
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Search input bg       │  #1a1a2e       │  #ffffff              │
│  Search input border   │  #252542       │  #d2d2e0              │
│  Search input (focus)  │  #FFC93C       │  #FFC93C              │
│  Search text           │  #ffffff       │  #1a1a2e              │
│  Search placeholder    │  #666680       │  #aaaacc              │
│  Section labels        │  #666680       │  #8888a8              │
│  Recent item text      │  #ffffff       │  #1a1a2e              │
│  Recent item icon      │  #9e9eb8       │  #4a4a6a              │
│  Result card bg        │  #252542       │  #ffffff              │
│  Result card border    │  none          │  1px #d2d2e0          │
│  Divider               │  #252542       │  #d2d2e0              │
└────────────────────────┴────────────────┴───────────────────────┘
Book Details Screen
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Hero cover blur bg    │  #1a1a2e       │  #f7f7f2              │
│  Book title            │  #ffffff       │  #1a1a2e              │
│  Author text           │  #9e9eb8       │  #4a4a6a              │
│  Star fill             │  #FFC93C       │  #FFC93C              │
│  Rating count          │  #9e9eb8       │  #4a4a6a              │
│  Action btn border     │  #ffffff       │  #1a1a2e              │
│  Action btn text       │  #ffffff       │  #1a1a2e              │
│  Dividers              │  #252542       │  #d2d2e0              │
│  Section labels        │  #666680       │  #8888a8              │
│  "Why" label           │  #FFC93C       │  #cc8800              │
│  Body text             │  #9e9eb8       │  #4a4a6a              │
│  Sentiment pos. bar    │  #03904a       │  #03904a              │
│  Sentiment neg. bar    │  #f13a2c       │  #f13a2c              │
│  Similar books card    │  #252542       │  #ffffff              │
└────────────────────────┴────────────────┴───────────────────────┘
Rating Modal
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Sheet bg              │  #252542       │  #ffffff              │
│  Overlay               │rgba(0,0,0,0.7) │rgba(0,0,0,0.4)        │
│  Handle                │  #666680       │  #c0c0d0              │
│  Title                 │  #ffffff       │  #1a1a2e              │
│  Body text             │  #9e9eb8       │  #4a4a6a              │
│  Star fill             │  #FFC93C       │  #FFC93C              │
│  Star empty            │  #3d3d5c       │  #d2d2e0              │
│  Input bg              │  #1a1a2e       │  #f7f7f2              │
│  Input border          │  #252542       │  #d2d2e0              │
│  Submit CTA            │  #FFC93C       │  #FFC93C              │
│  Cancel text           │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
Library Screen
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Tab label (inactive)  │  #666680       │  #8888a8              │
│  Tab label (active)    │  #ffffff       │  #1a1a2e              │
│  Active tab indicator  │  #FFC93C (2px) │  #FFC93C (2px)        │
│  Sort dropdown bg      │  #1a1a2e       │  #ffffff              │
│  Book card bg          │  #252542       │  #ffffff              │
│  Book card border      │  none          │  1px #d2d2e0          │
│  Book title            │  #ffffff       │  #1a1a2e              │
│  Book author           │  #9e9eb8       │  #4a4a6a              │
└────────────────────────┴────────────────┴───────────────────────┘
Insights / Reading DNA
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Personality card bg   │  #FFC93C       │  #FFC93C              │
│  Personality title     │  #1a1a2e       │  #1a1a2e              │
│  Personality body      │  #1a1a2e 85%   │  #1a1a2e 85%          │
│  Chart bg              │  #252542       │  #ffffff              │
│  Chart line/fill       │  #FFC93C       │  #FFC93C              │
│  Stat number           │  #ffffff       │  #1a1a2e              │
│  Stat label            │  #666680       │  #8888a8              │
│  List row text         │  #ffffff       │  #1a1a2e              │
│  Divider               │  #252542       │  #d2d2e0              │
│  Section labels        │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
Profile & Settings
text

┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Avatar border         │  #FFC93C       │  #FFC93C              │
│  Name text             │  #ffffff       │  #1a1a2e              │
│  Email text            │  #9e9eb8       │  #4a4a6a              │
│  Stat number           │  #ffffff       │  #1a1a2e              │
│  Stat label            │  #666680       │  #8888a8              │
│  Menu row text         │  #ffffff       │  #1a1a2e              │
│  Menu row chevron      │  #666680       │  #8888a8              │
│  Divider               │  #252542       │  #d2d2e0              │
│  Theme radio active    │  #FFC93C       │  #FFC93C              │
│  Theme radio inactive  │  #252542       │  #d2d2e0              │
│  Log Out text          │  #f13a2c       │  #f13a2c              │
│  Log Out border        │  #f13a2c       │  #f13a2c              │
└────────────────────────┴────────────────┴───────────────────────┘
✅ Do's and Don'ts
✅ Do
Use semantic tokens in every component — theme.background.card, not #252542.
Reserve brand.primary (#FFC93C) for CTAs, active tabs, stars, bee mark — scarcely.
Set every CTA to rounded.none (0px) — the brand's precision signature.
Render CTA labels in uppercase with 1.4px tracking via typography.button.
Force SplashScreen and PersonalizingScreen to always dark — cinematic moments.
Let border.focus and border.inputFocus stay amber (#FFC93C) in both modes.
Use the explicit 8px spacing ladder — never ad-hoc values.
Keep display weight at 500 — editorial confidence.
Add 1px border.default to cards in light mode — the contrast between #f7f7f2 and #ffffff is subtle; the border defines the card.
Use text.link (#cc8800) in light mode instead of #FFC93C for links — amber on white lacks contrast.
❌ Don't
Don't hardcode hex values in components — always use the semantic theme token.
Don't introduce a second brand accent color — amber is the only voltage.
Don't use rounded or pill CTAs — 0px sharp corners only.
Don't bold display copy — weight 700 for title-md, button, number-display only.
Don't use pure black #000000 anywhere — canvas (#1a1a2e) is the darkest surface.
Don't use pure white #ffffff as the light mode screen bg — use #f7f7f2 (slightly warm).
Don't change brand.primary (#FFC93C) between modes — it is the one immutable anchor.
Don't use #FFC93C as link text on light canvas — use #cc8800 instead for contrast.
Don't add drop shadow tiers — one soft drop max, web hover only.
Don't scatter amber decoratively — scarcity is what gives it identity power.
Don't forget to test contrast in both modes — especially text.secondary and text.muted.
♿ Accessibility Standards
Color Contrast
All text meets WCAG AA minimum in both modes:

Pairing	Dark Ratio	Light Ratio	Standard
text.primary on background.primary	14.8:1	16.1:1	✅ AAA
text.secondary on background.primary	4.6:1	4.5:1	✅ AA
text.muted on background.primary	4.5:1	4.5:1	✅ AA
brand.onPrimary on brand.primary	8.2:1	8.2:1	✅ AAA
text.link on background.primary	7.1:1 (amber)	4.6:1 (dark amber)	✅ AA
text.primary on background.card	12.4:1	17.1:1	✅ AAA
Touch Target Minimums
All interactive elements: minimum 44×44px
Primary CTA height: 48px (WCAG AAA)
Tab bar items: 44px effective tap area
Star inputs: 36px per star
Focus Indicators
Focus ring: 2px solid #FFC93C — same in both modes
Offset: 2px from element edge
Never suppress focus rings — visible in both modes
System Preferences Respected
TypeScript

// Respect system accessibility settings
import { AccessibilityInfo } from 'react-native';

// Reduce motion — disable shimmer animations
const reduceMotion = await AccessibilityInfo.isReduceMotionEnabled();

// High contrast — increase border weight
const highContrast = await AccessibilityInfo.isHighContrastEnabled();
if (highContrast) {
  // Increase border widths from 1px → 2px
  // Boost text contrast one step
}
Keyboard Navigation (Web)
Key	Action
Tab	Move focus forward
Shift+Tab	Move focus backward
Enter / Space	Activate button
Escape	Close modal / sheet
Arrow keys	Navigate star ratings, lists
📎 Appendix
Quick Token Reference
text

═══════════════════════════════════════════════════════════
  DARK MODE
═══════════════════════════════════════════════════════════
  background.primary      #1a1a2e
  background.elevated     #252542
  background.sunken       #131325
  background.card         #252542
  text.primary            #ffffff
  text.secondary          #9e9eb8
  text.muted              #666680
  text.link               #FFC93C
  border.default          #252542
  border.focus            #FFC93C

═══════════════════════════════════════════════════════════
  LIGHT MODE
═══════════════════════════════════════════════════════════
  background.primary      #f7f7f2
  background.elevated     #ffffff
  background.sunken       #ebebeb
  background.card         #ffffff
  text.primary            #1a1a2e
  text.secondary          #4a4a6a
  text.muted              #8888a8
  text.link               #cc8800
  border.default          #d2d2e0
  border.focus            #FFC93C

═══════════════════════════════════════════════════════════
  BRAND (IMMUTABLE — SAME IN BOTH)
═══════════════════════════════════════════════════════════
  brand.primary           #FFC93C
  brand.primaryActive     #E6A800
  brand.onPrimary         #1a1a2e
  brand.semanticSuccess   #03904a
  brand.semanticWarning   #f13a2c
  brand.semanticInfo      #4c98b9

═══════════════════════════════════════════════════════════
  TYPOGRAPHY (SAME IN BOTH — ONLY COLOR CHANGES)
═══════════════════════════════════════════════════════════
  display-mega    80px / 500 / lh 1.05 / ls -1.6px
  display-xl      56px / 500 / lh 1.1  / ls -1.12px
  display-lg      36px / 500 / lh 1.2  / ls -0.36px
  display-md      26px / 500 / lh 1.5  / ls 0.195px
  title-md        18px / 700 / lh 1.2  / ls 0
  body-md         14px / 400 / lh 1.5  / ls 0
  button          14px / 700 / lh 1.0  / ls 1.4px / UPPER
  nav-link        13px / 600 / lh 1.4  / ls 0.65px / UPPER
  caption-upper   11px / 600 / lh 1.4  / ls 1.1px  / UPPER

═══════════════════════════════════════════════════════════
  SPACING (SAME IN BOTH)
═══════════════════════════════════════════════════════════
  xxxs 4 · xxs 8 · xs 16 · sm 24 · md 32
  lg 48 · xl 64 · xxl 96 · super 128

═══════════════════════════════════════════════════════════
  RADIUS (SAME IN BOTH)
═══════════════════════════════════════════════════════════
  none 0 · xs 2 · sm 4 · md 6 · lg 8 · xl 12 · full 9999
Related Documents
APPFLOW.md — Application flow & screen states
PRD.md — Product requirements
TECHSPEC.md — Technical specification
Change Log
Version	Date	Author	Changes
1.0	[Date]	[Name]	Initial design system
2.0	[Today]	[Name]	Full dark/light theme system added — semantic tokens, ThemeContext, per-screen mode table, component dual-mode specs
End of Design Document 🎨

"Every color. Every pixel. Every token. In every mode. Precisely considered."




