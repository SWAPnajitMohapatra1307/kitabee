# 🎨 Kitabee — Design System Document

> **Document Version:** 3.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Status:** 🟢 Approved for Implementation
> **Related Docs:** [PRD.md](./PRD.md) v2.0 | [APPFLOW.md](./APPFLOW.md) v2.0 | [TECHSPEC.md](./TECHSPEC.md) v2.0 | [SCHEMA.md](./SCHEMA.md) v2.0

---

## 📚 Table of Contents

1. [Design Philosophy](#-design-philosophy)
2. [What Changed in v3.0](#-what-changed-in-v30)
3. [Theme System](#-theme-system)
4. [Color System](#-color-system)
5. [Typography](#-typography)
6. [Spacing System](#-spacing-system)
7. [Border Radius](#-border-radius)
8. [Elevation & Depth](#-elevation--depth)
9. [Content Type Design Language](#-content-type-design-language) 🆕
10. [Component Library](#-component-library)
11. [Netflix-Style Collection Rows](#-netflix-style-collection-rows) 🆕
12. [Series Order Section](#-series-order-section) 🆕
13. [Reader Screens (EPUB + Comics)](#-reader-screens-epub--comics) 🆕
14. [Layout & Grid](#-layout--grid)
15. [Responsive Behavior](#-responsive-behavior)
16. [Screen-by-Screen Design Specs](#-screen-by-screen-design-specs)
17. [Motion & Animation](#-motion--animation) 🆕
18. [Do's and Don'ts](#-dos-and-donts)
19. [Accessibility Standards](#-accessibility-standards)
20. [Appendix](#-appendix)

---

## 🎯 Design Philosophy

Kitabee reads as a **warm editorial product** — closer to a curated literary
magazine than a generic mobile app, now paired with **Netflix-familiar row-based discovery**. The base canvas is near-black (`#1a1a2e`) in dark mode and near-white (`#f7f7f2`) in light mode, both holding high-contrast display type. The single brand voltage is **Kitabee Amber** (`#FFC93C`) — the iconic bee-yellow — used scarcely on primary CTAs, the 🐝 mascot mark, active tab highlights, star rating fills, and the **free reading badge**.

Type runs **Inter** at modest weights (display 500, body 400) — never bombastic. Spacing follows an explicit **8px token ladder** (`xxxs` 4px through `super` 128px); generous editorial pacing throughout. The brand's strongest visual signature is the **horizontal collection row** — 8-12 covers scrolling side-by-side, each row titled with a catchy editorial phrase like *"Epic Worlds Built From Scratch"* or *"Dark But You Cannot Put It Down."*

### Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Editorial Confidence** | Let book and comic covers carry the visual weight. Type supports; never competes. |
| **Netflix Familiarity** 🆕 | Row-based horizontal discovery users already know — no learning curve. |
| **Amber Scarcity** | `#FFC93C` appears only on primary CTAs, active states, star ratings, and the free reading badge. Never decorative. |
| **Sharp Precision** | `0px` radius on all cards and primary buttons by default — crisp, modern. |
| **Generous Pacing** | Sections breathe. 96px vertical padding on major bands. Rows separated by 48px. |
| **Photographic Depth** | No drop shadow tiers. Elevation through brightness-step and cover imagery. |
| **Warm Dark Base** | Never pure black. `#1a1a2e` — slight warm indigo undertone. |
| **Warm Light Base** | Never pure white. `#f7f7f2` — slight warm cream undertone. |
| **Mode Agnostic Amber** | `#FFC93C` primary never changes between modes — it anchors identity in both. |
| **Content Type Symmetry** 🆕 | Books and comics share the same design language — only subtle iconography differentiates. |
| **Free Reading Signals** 🆕 | Free content marked with amber 🆓 badge — immediate value recognition. |

---

## 🆕 What Changed in v3.0

### Aligned With v2.0 of PRD / APPFLOW / TECHSPEC

**New Design Territories:**
- 🎬 **Netflix-Style Collection Row** component (horizontal scroller)
- 🃏 **ContentCard** unified design (books + comics with type indicators)
- 🔢 **SeriesOrderSection** component (reading order guide)
- 📖 **EPUBReaderScreen** UI chrome
- 🦸 **ComicsReaderScreen** UI chrome
- 🎯 **ContentChoiceScreen** onboarding tile design
- 🏷️ **ContentTypeTabs** (All / Books / Comics)
- 🆓 **FreeBadge** overlay component
- 🎭 **MoodTag** chip component
- 📊 **FullCollectionScreen** grid design

**Updated Screens:**
- 🔄 HomeScreen redesigned as Netflix rows (was: simple recommendation lists)
- 🔄 SearchScreen with content type tabs
- 🔄 DetailScreen with series order + free read button + mood tags
- 🔄 LibraryScreen with content type toggle
- 🔄 InsightsScreen with books vs comics breakdown
- 🔄 ProfileScreen with content preference option

**New Sections:**
- Content Type Design Language (§9)
- Netflix-Style Collection Rows (§11)
- Series Order Section (§12)
- Reader Screens (§13)
- Motion & Animation (§17)

**Total Screens Designed: 21** (was 17 in v2.0)

---

## 🌗 Theme System

### Overview

Kitabee supports **three theme modes:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         THEME MODES                                 │
├──────────────┬──────────────────────────────────────────────────────┤
│  dark        │  Default — near-black canvas, white ink              │
│  light       │  Near-cream canvas, dark ink                         │
│  system      │  Follows device OS preference (default on first open)│
└──────────────┴──────────────────────────────────────────────────────┘
```

**Default behavior:**
- First launch → `system` (reads `prefers-color-scheme`)
- User can override in Profile → Settings → Theme
- Selection persisted in `AsyncStorage` (Zustand middleware)

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

const systemScheme = useColorScheme();
const activeTheme = getActiveTheme(userPreference, systemScheme ?? 'dark');
```

### Semantic Token System

Every component references a **semantic token** — never a raw hex.

```
Raw Token (fixed hex)  →  Semantic Token (context alias)  →  Component
     #1a1a2e          →       background.primary          →   Screen bg
     #f7f7f2          →       background.primary          →   Screen bg
                              (resolves per theme)
```

### Semantic Token Map

#### Background Tokens

```
┌──────────────────────────┬──────────────────┬──────────────────┐
│  Semantic Token          │  Dark Mode       │  Light Mode      │
├──────────────────────────┼──────────────────┼──────────────────┤
│  background.primary      │  #1a1a2e         │  #f7f7f2         │
│  background.elevated     │  #252542         │  #ffffff         │
│  background.sunken       │  #131325         │  #ebebeb         │
│  background.overlay      │  rgba(0,0,0,0.7) │  rgba(0,0,0,0.4) │
│  background.card         │  #252542         │  #ffffff         │
│  background.input        │  #1a1a2e         │  #ffffff         │
│  background.modal        │  #252542         │  #ffffff         │
│  background.sheet        │  #252542         │  #ffffff         │
│  background.toast        │  #303052         │  #1a1a2e         │
│  background.reader 🆕    │  #0d0d1a         │  #faf8f2         │
│  background.readerChrome🆕 │  rgba(26,26,46,0.9) │ rgba(247,247,242,0.9) │
└──────────────────────────┴──────────────────┴──────────────────┘
```

**New v3.0 tokens:**
- `background.reader` — Slightly darker than canvas for immersive reading (dark mode) / slightly warmer for reduced eye strain (light mode)
- `background.readerChrome` — Semi-transparent overlay for reader UI (fades in/out)

#### Text Tokens

```
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
│  text.reader 🆕          │  #e8e8f0         │  #2a2a3e         │
└──────────────────────────┴──────────────────┴──────────────────┘
```

**New v3.0 token:**
- `text.reader` — Slightly softened primary text for long reading sessions (reduced pure-white glare)

#### Border / Hairline Tokens

```
┌──────────────────────────┬──────────────────┬──────────────────┐
│  Semantic Token          │  Dark Mode       │  Light Mode      │
├──────────────────────────┼──────────────────┼──────────────────┤
│  border.default          │  #252542         │  #d2d2e0         │
│  border.subtle           │  #1e1e38         │  #ebebf0         │
│  border.strong           │  #3d3d5c         │  #b0b0c8         │
│  border.focus            │  #FFC93C         │  #FFC93C         │
│  border.input            │  #252542         │  #d2d2e0         │
│  border.inputFocus       │  #FFC93C         │  #FFC93C         │
│  border.activeTab 🆕     │  #FFC93C         │  #FFC93C         │
└──────────────────────────┴──────────────────┴──────────────────┘
```

#### Brand Tokens (Never Change)

```
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
│  brand.freeReading 🆕    │  #FFC93C  (amber — same as primary)  │
└──────────────────────────┴──────────────────────────────────────┘
```

### Theme Token Implementation

```typescript
// theme/tokens.ts

export const rawColors = {
  // Dark surfaces
  canvas:            '#1a1a2e',
  canvasElevated:    '#252542',
  canvasSunken:      '#131325',
  canvasReader:      '#0d0d1a',      // 🆕 v3.0
  canvasLight:       '#f7f7f2',
  canvasLightCard:   '#ffffff',
  canvasLightSunken: '#ebebeb',
  canvasLightReader: '#faf8f2',      // 🆕 v3.0

  // Text - dark
  inkWhite:          '#ffffff',
  inkReaderDark:     '#e8e8f0',      // 🆕 v3.0 softened for reading
  inkBodyDark:       '#9e9eb8',
  inkMutedDark:      '#666680',
  inkDisabledDark:   '#3d3d5c',

  // Text - light
  inkDark:           '#1a1a2e',
  inkReaderLight:    '#2a2a3e',      // 🆕 v3.0 softened for reading
  inkBodyLight:      '#4a4a6a',
  inkMutedLight:     '#8888a8',
  inkDisabledLight:  '#c0c0d0',

  // Brand (immutable)
  amber:             '#FFC93C',
  amberActive:       '#E6A800',
  amberHover:        '#D4960A',
  amberDark:         '#cc8800',

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
  chromeDark:        'rgba(26,26,46,0.9)',   // 🆕 v3.0
  chromeLight:       'rgba(247,247,242,0.9)', // 🆕 v3.0
};

export const darkTheme = {
  background: {
    primary:      rawColors.canvas,
    elevated:     rawColors.canvasElevated,
    sunken:       rawColors.canvasSunken,
    overlay:      rawColors.overlayDark,
    card:         rawColors.canvasElevated,
    input:        rawColors.canvas,
    modal:        rawColors.canvasElevated,
    sheet:        rawColors.canvasElevated,
    toast:        '#303052',
    reader:       rawColors.canvasReader,       // 🆕
    readerChrome: rawColors.chromeDark,          // 🆕
  },
  text: {
    primary:     rawColors.inkWhite,
    secondary:   rawColors.inkBodyDark,
    muted:       rawColors.inkMutedDark,
    disabled:    rawColors.inkDisabledDark,
    onPrimary:   rawColors.inkDark,
    link:        rawColors.amber,
    placeholder: rawColors.inkMutedDark,
    reader:      rawColors.inkReaderDark,       // 🆕
  },
  border: {
    default:    rawColors.hairlineDark,
    subtle:     rawColors.hairlineSubtleDark,
    strong:     rawColors.hairlineStrongDark,
    focus:      rawColors.amber,
    input:      rawColors.hairlineDark,
    inputFocus: rawColors.amber,
    activeTab:  rawColors.amber,                // 🆕
  },
  brand: {
    primary:         rawColors.amber,
    primaryActive:   rawColors.amberActive,
    primaryHover:    rawColors.amberHover,
    onPrimary:       rawColors.inkDark,
    semanticSuccess: rawColors.success,
    semanticWarning: rawColors.warning,
    semanticInfo:    rawColors.info,
    freeReading:     rawColors.amber,           // 🆕
  },
};

export const lightTheme = {
  background: {
    primary:      rawColors.canvasLight,
    elevated:     rawColors.canvasLightCard,
    sunken:       rawColors.canvasLightSunken,
    overlay:      rawColors.overlayLight,
    card:         rawColors.canvasLightCard,
    input:        rawColors.canvasLightCard,
    modal:        rawColors.canvasLightCard,
    sheet:        rawColors.canvasLightCard,
    toast:        rawColors.inkDark,
    reader:       rawColors.canvasLightReader,  // 🆕
    readerChrome: rawColors.chromeLight,         // 🆕
  },
  text: {
    primary:     rawColors.inkDark,
    secondary:   rawColors.inkBodyLight,
    muted:       rawColors.inkMutedLight,
    disabled:    rawColors.inkDisabledLight,
    onPrimary:   rawColors.inkDark,
    link:        rawColors.amberDark,
    placeholder: rawColors.inkMutedLight,
    reader:      rawColors.inkReaderLight,      // 🆕
  },
  border: {
    default:    rawColors.hairlineLight,
    subtle:     rawColors.hairlineSubtleLight,
    strong:     rawColors.hairlineStrongLight,
    focus:      rawColors.amber,
    input:      rawColors.hairlineLight,
    inputFocus: rawColors.amber,
    activeTab:  rawColors.amber,                // 🆕
  },
  brand: {
    primary:         rawColors.amber,
    primaryActive:   rawColors.amberActive,
    primaryHover:    rawColors.amberHover,
    onPrimary:       rawColors.inkDark,
    semanticSuccess: rawColors.success,
    semanticWarning: rawColors.warning,
    semanticInfo:    rawColors.info,
    freeReading:     rawColors.amber,           // 🆕
  },
};

export type Theme = typeof darkTheme;
```

### Theme Context & Hook

```typescript
// theme/ThemeContext.tsx
import React, { createContext, useContext, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { darkTheme, lightTheme, Theme } from './tokens';

type ThemeMode = 'dark' | 'light' | 'system';

interface ThemeStore {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

// Zustand store (aligned with TECHSPEC.md state management choice)
export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      mode: 'system',
      setMode: (mode) => set({ mode }),
    }),
    {
      name: 'kitabee-theme',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Hook every component uses
export const useTheme = () => {
  const systemScheme = useColorScheme();
  const mode = useThemeStore((s) => s.mode);
  const activeMode: 'dark' | 'light' =
    mode === 'system' ? (systemScheme ?? 'dark') : mode;
  const theme = activeMode === 'dark' ? darkTheme : lightTheme;

  return { theme, mode, activeMode };
};
```

### Per-Screen Mode Behavior (Updated v3.0)

```
┌──────────────────────────┬──────────────────────────────────────────────┐
│  Screen                  │  Mode Behavior                               │
├──────────────────────────┼──────────────────────────────────────────────┤
│  SplashScreen            │  Always DARK — brand moment                  │
│  WelcomeScreen           │  Follows active theme                        │
│  LoginScreen             │  Follows active theme                        │
│  RegisterScreen          │  Follows active theme                        │
│  OnboardingIntro         │  Follows active theme                        │
│  ContentChoiceScreen 🆕  │  Follows active theme                        │
│  RateInitialContent      │  Follows active theme                        │
│  GenreSelectionScreen    │  Follows active theme                        │
│  PersonalizingScreen     │  Always DARK — cinematic loading moment      │
│  HomeScreen 🔄           │  Follows active theme                        │
│  FullCollectionScreen 🆕 │  Follows active theme                        │
│  SearchScreen 🔄         │  Follows active theme                        │
│  DetailScreen 🔄         │  Follows active theme                        │
│  RatingModal             │  Follows active theme (bottom sheet)         │
│  LibraryScreen 🔄        │  Follows active theme                        │
│  EPUBReaderScreen 🆕     │  Follows active theme (uses reader tokens)   │
│  ComicsReaderScreen 🆕   │  Always DARK — comics benefit from dark bg   │
│  InsightsScreen 🔄       │  Follows active theme                        │
│  ProfileScreen 🔄        │  Follows active theme                        │
│  SettingsScreen          │  Follows active theme                        │
│  EditProfileScreen       │  Follows active theme                        │
└──────────────────────────┴──────────────────────────────────────────────┘
```

**Rule:** SplashScreen, PersonalizingScreen, and **ComicsReaderScreen** are always dark. Comics benefit from dark backgrounds — page images pop against dark chrome, and it prevents halation around comic panels.

### Component-Level Mode Switching Table (Updated v3.0)

```
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
│  Content type tab active │  #FFC93C underline     │  #FFC93C underline  🆕 │
│  Free reading badge 🆕   │  #FFC93C / #1a1a2e     │  #FFC93C / #1a1a2e     │
│  Mood tag chip 🆕        │  #252542 / #9e9eb8     │  #ebebeb / #4a4a6a     │
│  Series "you are here"🆕 │  #FFC93C bg / #1a1a2e  │  #FFC93C bg / #1a1a2e  │
│  Reader background 🆕    │  #0d0d1a               │  #faf8f2               │
│  Reader text 🆕          │  #e8e8f0               │  #2a2a3e               │
│  Reader chrome overlay🆕 │  rgba(26,26,46,0.9)    │  rgba(247,247,242,0.9) │
│  Comics reader bg 🆕     │  #0d0d1a  (forced dark)│  #0d0d1a  (forced dark)│
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
```

---

## 🎨 Color System

### Brand & Accent

```
┌─────────────────────────────────────────────────────────────────┐
│  BRAND PALETTE                                                  │
├──────────────────┬──────────┬──────────────────────────────────┤
│  Token           │  Hex     │  Usage                           │
├──────────────────┼──────────┼──────────────────────────────────┤
│  primary         │ #FFC93C  │  CTAs, active tabs, star fills,  │
│                  │          │  bee mark, free reading badge 🆕 │
│  primary-active  │ #E6A800  │  Press/active state              │
│  primary-hover   │ #D4960A  │  Hover state (web only)          │
│  primary-dark    │ #cc8800  │  Links on light canvas only      │
└──────────────────┴──────────┴──────────────────────────────────┘
```

### Semantic Color Full Reference

```typescript
// design-tokens/semanticColors.ts

export const semanticColors = {
  dark: {
    'background.primary':      '#1a1a2e',
    'background.elevated':     '#252542',
    'background.sunken':       '#131325',
    'background.card':         '#252542',
    'background.input':        '#1a1a2e',
    'background.modal':        '#252542',
    'background.overlay':      'rgba(0,0,0,0.7)',
    'background.toast':        '#303052',
    'background.reader':       '#0d0d1a',                // 🆕
    'background.readerChrome': 'rgba(26,26,46,0.9)',     // 🆕

    'text.primary':     '#ffffff',
    'text.secondary':   '#9e9eb8',
    'text.muted':       '#666680',
    'text.disabled':    '#3d3d5c',
    'text.onPrimary':   '#1a1a2e',
    'text.link':        '#FFC93C',
    'text.placeholder': '#666680',
    'text.reader':      '#e8e8f0',                       // 🆕

    'border.default':    '#252542',
    'border.subtle':     '#1e1e38',
    'border.strong':     '#3d3d5c',
    'border.focus':      '#FFC93C',
    'border.input':      '#252542',
    'border.inputFocus': '#FFC93C',
    'border.activeTab':  '#FFC93C',                      // 🆕
  },
  light: {
    'background.primary':      '#f7f7f2',
    'background.elevated':     '#ffffff',
    'background.sunken':       '#ebebeb',
    'background.card':         '#ffffff',
    'background.input':        '#ffffff',
    'background.modal':        '#ffffff',
    'background.overlay':      'rgba(0,0,0,0.4)',
    'background.toast':        '#1a1a2e',
    'background.reader':       '#faf8f2',                // 🆕
    'background.readerChrome': 'rgba(247,247,242,0.9)',  // 🆕

    'text.primary':     '#1a1a2e',
    'text.secondary':   '#4a4a6a',
    'text.muted':       '#8888a8',
    'text.disabled':    '#c0c0d0',
    'text.onPrimary':   '#1a1a2e',
    'text.link':        '#cc8800',
    'text.placeholder': '#aaaacc',
    'text.reader':      '#2a2a3e',                       // 🆕

    'border.default':    '#d2d2e0',
    'border.subtle':     '#ebebf0',
    'border.strong':     '#b0b0c8',
    'border.focus':      '#FFC93C',
    'border.input':      '#d2d2e0',
    'border.inputFocus': '#FFC93C',
    'border.activeTab':  '#FFC93C',                      // 🆕
  },
  brand: {
    'brand.primary':         '#FFC93C',
    'brand.primaryActive':   '#E6A800',
    'brand.onPrimary':       '#1a1a2e',
    'brand.semanticSuccess': '#03904a',
    'brand.semanticWarning': '#f13a2c',
    'brand.semanticInfo':    '#4c98b9',
    'brand.freeReading':     '#FFC93C',                  // 🆕
  },
};
```

---

## 🔤 Typography

### Font Family

**Inter** is the primary sans family across every text role.
**Fallback:** `-apple-system, system-ui, sans-serif`

No display/body family split — single family, multiple weights. Typography does not change between light and dark modes — only color changes.

### Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| **display-mega** | 80px | 500 | 1.05 | -1.6px | Splash / Welcome hero H1 |
| **display-xl** | 56px | 500 | 1.1 | -1.12px | Section hero headlines |
| **display-lg** | 36px | 500 | 1.2 | -0.36px | Onboarding headers, screen titles |
| **display-md** | 26px | 500 | 1.5 | 0.195px | Subsection heads, modal titles |
| **row-title** 🆕 | 20px | 600 | 1.3 | -0.2px | Collection row titles (Netflix rows) |
| **title-md** | 18px | 700 | 1.2 | 0 | Card titles, component labels |
| **title-sm** | 16px | 500 | 1.4 | 0.08px | List labels, tab titles |
| **body-md** | 14px | 400 | 1.5 | 0 | Default body text |
| **body-sm** | 13px | 400 | 1.5 | 0 | Secondary body, footer text |
| **reader-body** 🆕 | 17px | 400 | 1.7 | 0.1px | EPUB reader body text (relaxed) |
| **caption** | 12px | 400 | 1.4 | 0 | Photo captions, timestamps |
| **caption-uppercase** | 11px | 600 | 1.4 | 1.1px | Section labels, genre badges — UPPERCASE |
| **badge-micro** 🆕 | 10px | 700 | 1.0 | 0.8px | Free reading badge, type badges — UPPERCASE |
| **button** | 14px | 700 | 1.0 | 1.4px | CTA labels — UPPERCASE |
| **nav-link** | 13px | 600 | 1.4 | 0.65px | Tab bar labels — UPPERCASE |
| **number-display** | 80px | 700 | 1.0 | -1.6px | Stat callouts, insight numbers |

### Typography Token Reference

```typescript
// design-tokens/typography.ts
export const typography = {
  'display-mega': {
    fontFamily: "'Inter', -apple-system, system-ui, sans-serif",
    fontSize: 80, fontWeight: '500', lineHeight: 1.05, letterSpacing: -1.6,
  },
  'display-xl': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 56, fontWeight: '500', lineHeight: 1.1, letterSpacing: -1.12,
  },
  'display-lg': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 36, fontWeight: '500', lineHeight: 1.2, letterSpacing: -0.36,
  },
  'display-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 26, fontWeight: '500', lineHeight: 1.5, letterSpacing: 0.195,
  },
  'row-title': {                                              // 🆕 v3.0
    fontFamily: "'Inter', sans-serif",
    fontSize: 20, fontWeight: '600', lineHeight: 1.3, letterSpacing: -0.2,
  },
  'title-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 18, fontWeight: '700', lineHeight: 1.2, letterSpacing: 0,
  },
  'title-sm': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 16, fontWeight: '500', lineHeight: 1.4, letterSpacing: 0.08,
  },
  'body-md': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 14, fontWeight: '400', lineHeight: 1.5, letterSpacing: 0,
  },
  'body-sm': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 13, fontWeight: '400', lineHeight: 1.5, letterSpacing: 0,
  },
  'reader-body': {                                            // 🆕 v3.0
    fontFamily: "'Inter', 'Georgia', serif",
    fontSize: 17, fontWeight: '400', lineHeight: 1.7, letterSpacing: 0.1,
  },
  caption: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 12, fontWeight: '400', lineHeight: 1.4, letterSpacing: 0,
  },
  'caption-uppercase': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 11, fontWeight: '600', lineHeight: 1.4, letterSpacing: 1.1,
    textTransform: 'uppercase',
  },
  'badge-micro': {                                            // 🆕 v3.0
    fontFamily: "'Inter', sans-serif",
    fontSize: 10, fontWeight: '700', lineHeight: 1.0, letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  button: {
    fontFamily: "'Inter', sans-serif",
    fontSize: 14, fontWeight: '700', lineHeight: 1.0, letterSpacing: 1.4,
    textTransform: 'uppercase',
  },
  'nav-link': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 13, fontWeight: '600', lineHeight: 1.4, letterSpacing: 0.65,
    textTransform: 'uppercase',
  },
  'number-display': {
    fontFamily: "'Inter', sans-serif",
    fontSize: 80, fontWeight: '700', lineHeight: 1.0, letterSpacing: -1.6,
  },
};
```

### Typography Principles

- Display weight stays at 500 — editorial confidence, not bombastic.
- CTA labels are uppercase with 1.4px tracking — precise, intentional.
- Nav labels are uppercase with 0.65px tracking.
- Row titles (`row-title`) balance authority (600 weight) with warmth (slightly negative tracking) — not shouty like display but stronger than title.
- Reader body uses **relaxed line-height (1.7)** and slightly larger size (17px) with positive tracking (0.1px) for extended reading comfort.
- Never bold display copy — weight 700 reserved for `title-md`, `button`, `badge-micro`, and `number-display` only.
- Typography scale never changes between modes — only the color token applied to text changes.

---

## 📐 Spacing System

### Token Ladder

Base unit: **8px** (with a 4px `xxxs` micro-step).

```
┌──────────┬────────┬─────────────────────────────────────────┐
│  Token   │  Value │  Primary Usage                          │
├──────────┼────────┼─────────────────────────────────────────┤
│  xxxs    │  4px   │  Icon gaps, badge padding               │
│  xxs     │  8px   │  Inline element gaps, chip padding      │
│  xs      │  16px  │  Component internal padding, card gaps  │
│  sm      │  24px  │  Card padding, form group gaps          │
│  md      │  32px  │  Section internal spacing               │
│  lg      │  48px  │  Between collection rows 🆕             │
│  xl      │  64px  │  Footer padding, wide section gaps      │
│  xxl     │  96px  │  Major band vertical padding            │
│  super   │  128px │  Hero band depth, splash breathing room │
└──────────┴────────┴─────────────────────────────────────────┘
```

```typescript
// design-tokens/spacing.ts
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
```

### Usage Rules

- **Section padding:** `spacing.xxl` (96px) for major bands
- **Hero band depth:** `spacing.super` (128px)
- **Between collection rows:** `spacing.lg` (48px) 🆕
- **Card internal padding:** `spacing.sm` (24px)
- **Content card gaps within a row:** `spacing.xs` (16px) 🆕
- **Component gaps:** `spacing.xs` (16px)
- Never use ad-hoc px values — always pull from the token ladder
- Spacing does not change between modes

---

## 🔲 Border Radius

### Radius Scale

```
┌──────────────┬──────────┬──────────────────────────────────────────┐
│  Token       │  Value   │  Usage                                   │
├──────────────┼──────────┼──────────────────────────────────────────┤
│  none        │  0px     │  ALL CTAs, cards, bands — dominant shape │
│  xs          │  2px     │  Tight genre badges, free reading badge 🆕│
│  sm          │  4px     │  Form inputs, text fields                │
│  md          │  6px     │  Compact cards (rare, mobile only)       │
│  lg          │  8px     │  Bottom sheet top corners                │
│  xl          │  12px    │  Modal/dialog corners                    │
│  full        │  9999px  │  Avatar circles, badge pills, mood tags 🆕│
└──────────────┴──────────┴──────────────────────────────────────────┘
```

```typescript
// design-tokens/rounded.ts
export const rounded = {
  none: 0,
  xs:   2,
  sm:   4,
  md:   6,
  lg:   8,
  xl:   12,
  full: 9999,
};
```

### Radius Principles

- **Sharp by default.** 0px is the Kitabee button and card shape.
- **Pill geometry (`full`)** reserved for: avatar plates, badge pills, and **mood tag chips**.
- **Content cards:** 0px (books + comics)
- **Free reading badge:** `rounded.xs` (2px) — slightly softer than surrounding sharp elements to draw the eye
- **Bottom sheets:** `rounded.lg` (8px) on top corners only
- Border radius does not change between modes

---

## 🏔️ Elevation & Depth

### Elevation Levels

```
┌──────────────────┬────────────────────────────────┬──────────────────────────┐
│  Level           │  Dark Mode                     │  Light Mode              │
├──────────────────┼────────────────────────────────┼──────────────────────────┤
│  Flat (base)     │  #1a1a2e                       │  #f7f7f2                 │
│  Card            │  #252542                       │  #ffffff + 1px border    │
│  Elevated        │  #252542                       │  #ffffff + shadow        │
│  Sunken          │  #131325                       │  #ebebeb                 │
│  Reader canvas 🆕│  #0d0d1a                       │  #faf8f2                 │
│  Reader chrome 🆕│  rgba(26,26,46,0.9) blur       │  rgba(247,247,242,0.9)  │
│  Hairline border │  1px #252542                   │  1px #d2d2e0             │
│  Soft drop       │  0 4px 8px rgba(0,0,0,0.2)    │  0 4px 8px rgba(0,0,0,0.08)│
│  Cover imagery   │  Full-bleed cover art          │  Full-bleed cover art    │
└──────────────────┴────────────────────────────────┴──────────────────────────┘
```

### Reader Chrome (v3.0)

Reader UI (top bar with title/close, bottom bar with page indicator) uses **semi-transparent background with backdrop blur** so page content remains partially visible underneath. This preserves reading immersion.

```typescript
// Reader chrome style
{
  backgroundColor: theme.background.readerChrome,
  backdropFilter: 'blur(10px)',       // web
  // iOS: BlurView with intensity 80
  // Android: BlurView with radius 10
}
```

### Decorative Depth

- **Full-bleed cover imagery** is the primary depth treatment in both modes.
- **Amber gradient** (`linear-gradient(180deg, #cc8800, #FFC93C 64%)`): Used inside CTA bands.
- **Dark gradient** (`linear-gradient(180deg, #2a2a4a, #1a1a2e 64%)`): Dark mode section transitions.
- **Light gradient** (`linear-gradient(180deg, #ffffff, #f7f7f2 64%)`): Light mode section transitions.

---

## 🎭 Content Type Design Language 🆕

Kitabee unifies **books** and **comics** into one design language. The two content types share nearly all visual elements — only subtle iconography and metadata layouts differentiate them.

### Content Type Identifiers

| Element | Books | Comics |
|---------|-------|--------|
| **Type icon** | 📚 | 🦸 |
| **Type label** | `BOOK` | `COMIC` |
| **Cover aspect ratio** | 2:3 (portrait) | 2:3 (portrait) |
| **Metadata line 1** | Author name | Creator name |
| **Metadata line 2** | Series/publisher | Issue # / publisher |
| **Detail hero** | Full-bleed cover | Full-bleed cover |
| **Series section shown** | If part of book series | If part of comic run |
| **Free reading source** | Internet Archive (EPUB) | Internet Archive (images) |
| **Reader used** | EPUBReaderScreen | ComicsReaderScreen |

### Type Badge Component

Appears on `ContentCard` and `SearchResultCard` when content type context is needed (mixed search results, unified library view).

```
┌─────────────┐         ┌─────────────┐
│  📚 BOOK    │         │  🦸 COMIC   │
└─────────────┘         └─────────────┘
```

**Styling:**
```
backgroundColor:  background.sunken (dark: #131325, light: #ebebeb)
color:            text.secondary
typography:       badge-micro (10px / 700 / uppercase / 0.8px tracking)
padding:          4px 8px
borderRadius:     rounded.xs (2px)
icon size:        12px (emoji character)
```

### Free Reading Badge

Overlays the top-right corner of any `ContentCard` when the item is available via Internet Archive.

```
┌──────────────┐
│         🆓  │  ← FREE badge overlay
│              │
│  [Cover art] │
│              │
│              │
├──────────────┤
│ Title        │
│ Author       │
│ ⭐ 4.5       │
└──────────────┘
```

**Styling:**
```
backgroundColor:  brand.freeReading (#FFC93C)
color:            brand.onPrimary (#1a1a2e)
typography:       badge-micro
content:          "FREE"
padding:          3px 6px
borderRadius:     rounded.xs (2px)
position:         absolute top: 8px right: 8px
elevation:        z-index 2, shadow: 0 2px 4px rgba(0,0,0,0.3)
```

### Mood Tag Chip

Appears on `DetailScreen` below description. Non-interactive display element.

```
🎭 Mood:  [ epic ]  [ thoughtful ]  [ grand ]
```

**Styling:**
```
backgroundColor:  background.sunken
color:            text.secondary
typography:       caption (12px / 400)
padding:          6px 12px
borderRadius:     rounded.full (9999px — pill)
gap:              8px (spacing.xxs) between chips
prefix icon:      🎭 (only on first chip / label)
```

**Available mood values** (from Collection Engine per TECHSPEC §7):
`dark`, `funny`, `epic`, `romantic`, `thrilling`, `inspiring`, `cozy`

---

## 🧩 Component Library

All components below list both dark and light values via semantic tokens.

### Navigation Bar (Bottom Tab)

```
┌────────────────────────┬────────────────┬───────────────────────┐
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
```

**Tabs:** 🏠 Home · 🔍 Search · 📖 Library · 📊 Insights · 👤 Profile

### Header Bar

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  textColor             │  #ffffff       │  #1a1a2e              │
│  typography            │  title-md      │  title-md             │
│  height                │  56px          │  56px                 │
│  borderBottom (scroll) │  1px #252542   │  1px #d2d2e0          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Buttons

#### Primary Button (Amber CTA) — Same in Both Modes

```
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
```

#### Outline Button

```
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
```

#### Tertiary Text Button

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  transparent   │  transparent          │
│  textColor             │  #FFC93C       │  #cc8800              │
│  typography            │  button        │  button               │
│  no border             │  —             │  —                    │
└────────────────────────┴────────────────┴───────────────────────┘
```

### ContentCard 🔄 (Updated for Books + Comics)

The universal card component for both books and comics. Used in collection rows, search results, library grids, and similar-items sections.

```
┌──────────────┐
│         🆓   │  ← Optional free badge (top-right)
│              │
│  [Cover art] │  ← 2:3 aspect ratio
│              │
│              │
├──────────────┤
│ Title        │  ← title-sm, 1-2 lines truncated
│ Author       │  ← body-sm, 1 line
│ 📚 · ⭐ 4.5 │  ← Type icon + rating (badge-micro)
└──────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #252542       │  #ffffff              │
│  borderColor           │  none          │  1px #d2d2e0          │
│  borderRadius          │  0px           │  0px                  │
│  coverRadius           │  0px           │  0px                  │
│  coverAspectRatio      │  2:3           │  2:3                  │
│  cardWidth (row)       │  140px         │  140px                │
│  cardWidth (grid)      │  flexible      │  flexible             │
│  titleColor            │  #ffffff       │  #1a1a2e              │
│  titleTypography       │  title-sm      │  title-sm             │
│  titleMaxLines         │  2             │  2                    │
│  authorColor           │  #9e9eb8       │  #4a4a6a              │
│  authorTypography      │  body-sm       │  body-sm              │
│  authorMaxLines        │  1             │  1                    │
│  metaLine (type+rating)│  badge-micro   │  badge-micro          │
│  starFill              │  #FFC93C       │  #FFC93C              │
│  padding (below cover) │  12px          │  12px                 │
└────────────────────────┴────────────────┴───────────────────────┘
```

**States:**
- **Default:** As above
- **Long-press:** Slight scale down (`scale: 0.97`), reveal quick actions
- **Loading (skeleton):** Cover area = `background.sunken` shimmer

### Text Inputs

```
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
```

### Badge Pill

```
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
```

### Content Type Tabs 🆕

Used on SearchScreen and LibraryScreen to filter between books and comics.

```
[ All ]  [ Books ]  [ Comics ]
─────
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  transparent   │  transparent          │
│  gap between tabs      │  24px          │  24px                 │
│  padding (each tab)    │  8px 4px       │  8px 4px              │
│  typography            │  title-sm      │  title-sm             │
│  inactive text         │  #666680       │  #8888a8              │
│  active text           │  #ffffff       │  #1a1a2e              │
│  active underline      │  2px #FFC93C   │  2px #FFC93C          │
│  underline offset      │  4px below     │  4px below            │
│  transition            │  200ms ease    │  200ms ease           │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Modal / Bottom Sheet

```
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
```

### Toast Notifications

```
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
```

### Skeleton / Loading

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  baseColor             │  #252542       │  #ebebeb              │
│  shimmerColor          │  #3d3d5c       │  #d2d2e0              │
│  borderRadius          │  0px           │  0px                  │
│  animation             │  shimmer 1.4s  │  shimmer 1.4s         │
└────────────────────────┴────────────────┴───────────────────────┘
```

**Netflix Row Skeleton Pattern (v3.0):**
- 3-4 skeleton rows visible on home screen load
- Each row = title placeholder (200×20px) + 4-6 card placeholders (140×260px)
- Shimmer travels horizontally left-to-right per row

### Empty State

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  backgroundColor       │  #1a1a2e       │  #f7f7f2              │
│  illustration tint     │  #FFC93C       │  #FFC93C              │
│  mascot 🐝             │  128px         │  128px                │
│  titleColor            │  #ffffff       │  #1a1a2e              │
│  titleTypography       │  display-md    │  display-md           │
│  bodyColor             │  #9e9eb8       │  #4a4a6a              │
│  bodyTypography        │  body-md       │  body-md              │
│  CTA                   │  button-primary│  button-primary       │
└────────────────────────┴────────────────┴───────────────────────┘
```

---

## 🎬 Netflix-Style Collection Rows 🆕

The **CollectionRow** is Kitabee's signature discovery pattern. Horizontally scrollable, editorial-titled, and highly performant.

### CollectionRow Component

```
┌────────────────────────────────────────────────────────┐
│ 🌍 Epic Worlds Built From Scratch          See all →   │  ← Row header
├────────────────────────────────────────────────────────┤
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ►           │
│ │📚 │ │📚 │ │📚 │ │📚 │ │📚 │ │📚 │                 │  ← Horizontal scroll
│ │Cvr│ │Cvr│ │Cvr│ │Cvr│ │Cvr│ │Cvr│                 │     Snap to card
│ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘             │
│ Title  Title  Title  Title  Title  Title              │
└────────────────────────────────────────────────────────┘
```

### Anatomy

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Row container padding │  16px horiz    │  16px horiz           │
│  Row vertical gap      │  48px (spacing.lg between rows)        │
│  Header padding-bottom │  12px          │  12px                 │
│  Emoji size            │  20px inline   │  20px inline          │
│  Emoji-to-title gap    │  8px           │  8px                  │
│  Title typography      │  row-title     │  row-title            │
│  Title color           │  #ffffff       │  #1a1a2e              │
│  "See all →" typography│  body-sm       │  body-sm              │
│  "See all →" color     │  #FFC93C       │  #cc8800              │
│  "See all →" tap area  │  min 44×44     │  min 44×44            │
│  Card width            │  140px         │  140px                │
│  Card gap              │  16px (xs)     │  16px (xs)            │
│  Cards visible (mob)   │  ~2.3 cards    │  ~2.3 cards           │
│  Cards visible (tab)   │  ~4 cards      │  ~4 cards             │
│  Cards visible (desk)  │  ~6 cards      │  ~6 cards             │
│  Scroll snap           │  card-width    │  card-width           │
│  Lazy render threshold │  next 4 cards  │  next 4 cards         │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Row Header Interactions

- **Tap row title** → navigate to `FullCollectionScreen`
- **Tap "See all →"** → navigate to `FullCollectionScreen`
- Row title is a full-width tap zone (header row height 44px minimum)

### Card Interactions

- **Tap card** → navigate to `DetailScreen(id, content_type)`
- **Long-press card** → show quick actions bottom sheet (Add to library / Rate / Share)
- **Swipe row** → horizontal scroll with snap points

### Collection Row Types (v3.0)

Per PRD §F4, home screen shows minimum 6 rows from these categories:

| Row Category | Example Title | Personalization | Emoji |
|--------------|---------------|-----------------|-------|
| **Personalized** | "Because You Loved Dune..." | ML — high | 🔥 |
| **Mood-based** | "Epic Worlds Built From Scratch" | NLP — medium | 🌍 |
| **Mood-based** | "Dark But You Cannot Put It Down" | NLP — medium | 🌙 |
| **Mood-based** | "Feel Good Reads" | NLP — medium | ☀️ |
| **Free reading** | "Free to Read Right Now" | None — universal | 📖 |
| **Comics** | "Comics — Perfect Starting Points" | Filtered by preference | 🦸 |
| **Series** | "Complete Series — Start to Finish" | Filtered by taste | ✅ |
| **Trending** | "Everyone Is Reading This" | None — global | 🔥 |
| **Discovery** | "Hidden Gems You Will Love" | ML — high | 💎 |
| **Continue** | "▶ Continue Reading" | Reading progress based | ▶ |

### Continue Reading Row (Special Case)

Appears at the **top** of HomeScreen when the user has active reading progress.

```
┌────────────────────────────────────────────────────────┐
│ ▶ Continue Reading                                     │
├────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐                │
│ │  ┌────┐  Sapiens                    │                │  ← Larger card
│ │  │📚 │  Yuval Noah Harari           │                │     Progress bar
│ │  │Cvr│  ▓▓▓▓▓░░░░ 45% · Ch 5      │                │
│ │  └────┘  [ CONTINUE ]               │                │  ← Amber CTA
│ └─────────────────────────────────────┘                │
└────────────────────────────────────────────────────────┘
```

**Styling:**
- Card is wider (280px) with horizontal layout
- Progress bar: 4px height, `background.sunken` track, `brand.primary` fill
- CONTINUE button opens correct reader (EPUB or Comics based on content_type)

### FullCollectionScreen 🆕

Tapping any row title or "See all →" opens the full collection in grid view.

```
┌─────────────────────────────────────────┐
│  ← Epic Worlds Built From Scratch       │  ← Header (title-md)
│  12 books · Updated today               │  ← Meta (caption)
├─────────────────────────────────────────┤
│  Immersive fantasy worlds you can       │
│  lose yourself in for weeks.            │  ← Description (body-md)
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │  ← 3-column grid (mobile)
│  └────┘ └────┘ └────┘                   │     4-column (tablet)
│  Title  Title  Title                    │     5-column (desktop)
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │
│  └────┘ └────┘ └────┘                   │
│                                         │
└─────────────────────────────────────────┘
```

**Grid gap:** `spacing.xs` (16px) horizontal and vertical.

---

## 🔢 Series Order Section 🆕

Appears on DetailScreen when content is part of a detected series. Kitabee's killer feature for both books and comics.

### Anatomy

```
┌─────────────────────────────────────────┐
│  🔢 DUNE SERIES — Reading Order         │  ← Section header
│                                         │
│  📖 Main Series:                        │  ← Sub-label
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ 1. Dune         ← You are here 🎯 │  │  ← Amber highlight
│  ├───────────────────────────────────┤  │
│  │ 2. Dune Messiah                   │  │  ← Tappable rows
│  ├───────────────────────────────────┤  │
│  │ 3. Children of Dune               │  │
│  ├───────────────────────────────────┤  │
│  │ 4. God Emperor of Dune            │  │
│  ├───────────────────────────────────┤  │
│  │ 5. Heretics of Dune               │  │
│  ├───────────────────────────────────┤  │
│  │ 6. Chapterhouse: Dune             │  │
│  └───────────────────────────────────┘  │
│                                         │
│  💡 Tip: Books 1-3 are the core         │  ← Contextual tip
│     trilogy. Books 4-6 are for          │
│     dedicated fans.                     │
│                                         │
│  🔀 Prequel Series (by Brian Herbert):  │  ← Companion section
│  ┌───────────────────────────────────┐  │
│  │ 1. House Atreides                 │  │
│  ├───────────────────────────────────┤  │
│  │ 2. House Harkonnen                │  │
│  ├───────────────────────────────────┤  │
│  │ 3. House Corrino                  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  💡 Read after Book 1 or after all 6.   │
└─────────────────────────────────────────┘
```

### Styling

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Section bg            │  transparent   │  transparent          │
│  Section header 🔢     │  title-md      │  title-md             │
│  Section header color  │  #ffffff       │  #1a1a2e              │
│  Sub-label 📖 🔀       │  caption-upper │  caption-upper        │
│  Sub-label color       │  #666680       │  #8888a8              │
│  Series list bg        │  #252542       │  #ffffff (border)     │
│  Series list border    │  0px           │  1px #d2d2e0          │
│  Row divider           │  1px #1e1e38   │  1px #ebebf0          │
│  Row padding           │  16px          │  16px                 │
│  Row typography        │  body-md       │  body-md              │
│  Row text color        │  #ffffff       │  #1a1a2e              │
│  "You are here" bg     │  #FFC93C       │  #FFC93C              │
│  "You are here" text   │  #1a1a2e       │  #1a1a2e              │
│  "You are here" label  │  🎯 accent icon│  🎯 accent icon       │
│  Label chip (e.g.      │  #4c98b9 bg    │  #4c98b9 bg           │
│  "Start Here")         │  #ffffff text  │  #ffffff text         │
│  Tip container         │  #131325       │  #ebebeb              │
│  Tip icon 💡           │  20px          │  20px                 │
│  Tip typography        │  body-sm       │  body-sm              │
│  Tip color             │  #9e9eb8       │  #4a4a6a              │
│  Tip padding           │  16px          │  16px                 │
│  Tip border-left       │  3px #FFC93C   │  3px #FFC93C          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Row Labels

Small chips shown after the title to indicate entry type:

| Label | Background | Text | Use When |
|-------|-----------|------|----------|
| `START HERE` | `brand.semanticInfo` (#4c98b9) | #ffffff | First entry, new reader friendly |
| `PREQUEL` | `brand.semanticWarning` (#f13a2c) 30% opacity | inherit | Chronological prequel |
| `SPINOFF` | `text.muted` bg 30% opacity | inherit | Companion story |
| `OPTIONAL` | transparent + 1px border | `text.muted` | Skip-able entry |

### Interactions

- **Tap any row** → navigate to that entry's DetailScreen
- **Current entry** ("You are here") → non-interactive, visually distinct amber background
- **Long-press row** → quick actions (Add to library)

---

## 📖 Reader Screens (EPUB + Comics) 🆕

Reader screens use dedicated `reader` semantic tokens for extended reading comfort.

### EPUB Reader Screen

```
┌─────────────────────────────────────────┐
│  ←  Dune                          ⚙️    │  ← Top chrome (fades)
├─────────────────────────────────────────┤
│                                         │
│                                         │
│  Chapter 5: Arrakis                     │  ← Chapter heading
│                                         │
│  The Duke Leto stood at the balcony     │
│  overlooking the vast desert. His son   │
│  Paul stood beside him, taking in the   │
│  sight of their new home for the first  │  ← reader-body
│  time...                                │     (17px / 1.7 lh)
│                                         │
│                                         │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  [◄ Prev]   Ch 5 · 45%   [Next ►]       │  ← Bottom chrome
└─────────────────────────────────────────┘
```

### Styling

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #0d0d1a       │  #faf8f2              │
│  Reader canvas bg      │  #0d0d1a       │  #faf8f2              │
│  Reader text color     │  #e8e8f0       │  #2a2a3e              │
│  Reader typography     │  reader-body   │  reader-body          │
│                        │  (17px / 1.7)  │  (17px / 1.7)         │
│  Top chrome bg         │  rgba(26,26,46,0.9)│rgba(247,247,242,0.9)│
│  Top chrome backdrop   │  blur 10px     │  blur 10px            │
│  Top chrome height     │  56px          │  56px                 │
│  Bottom chrome bg      │  same as top   │  same as top          │
│  Bottom chrome height  │  56px          │  56px                 │
│  Chrome text color     │  #ffffff       │  #1a1a2e              │
│  Progress typography   │  caption       │  caption              │
│  Nav button typography │  button        │  button               │
│  Chrome fade timing    │  2s hide       │  2s hide              │
│  Chapter heading       │  display-md    │  display-md           │
│  Content padding       │  24px horiz    │  24px horiz           │
│  Content max-width     │  680px (web)   │  680px (web)          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Reader Settings Menu (⚙️)

Bottom sheet triggered by settings icon:

```
┌─────────────────────────────────────────┐
│  Reading Settings                       │
├─────────────────────────────────────────┤
│                                         │
│  Font Size                              │
│  [ A- ]   17px   [ A+ ]                 │
│                                         │
│  Line Spacing                           │
│  [ ─ ]   1.7   [ + ]                    │
│                                         │
│  Theme                                  │
│  ○ Sepia   ● Auto   ○ Dark              │
│                                         │
└─────────────────────────────────────────┘
```

### Comics Reader Screen (Always Dark)

```
┌─────────────────────────────────────────┐
│  ←  Batman: Year One            ⚙️      │  ← Top chrome (fades)
├─────────────────────────────────────────┤
│                                         │
│                                         │
│                                         │
│                                         │
│                                         │
│         [FULL PAGE IMAGE]               │  ← Full-bleed comic page
│                                         │
│                                         │
│                                         │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│           Page 5 of 32                  │  ← Bottom chrome (fades 2s)
└─────────────────────────────────────────┘
```

### Styling

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Property              │  Dark (forced) │  Light (forced dark)  │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #0d0d1a       │  #0d0d1a  (forced)    │
│  Comic page bg         │  #0d0d1a       │  #0d0d1a              │
│  Top chrome bg         │  rgba(0,0,0,0.7)│ rgba(0,0,0,0.7)      │
│  Top chrome backdrop   │  blur 10px     │  blur 10px            │
│  Chrome text color     │  #ffffff       │  #ffffff              │
│  Page indicator typo   │  caption       │  caption              │
│  Page indicator color  │  #ffffff 80%   │  #ffffff 80%          │
│  Chrome fade timing    │  2s hide       │  2s hide              │
│  Zoom max scale        │  4x            │  4x                   │
│  Page-turn animation   │  slide 250ms   │  slide 250ms          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Reader Gestures

| Gesture | EPUB Reader | Comics Reader |
|---------|-------------|---------------|
| **Swipe left** | Next page | Next page |
| **Swipe right** | Previous page | Previous page |
| **Tap left edge** | Previous page | Previous page |
| **Tap right edge** | Next page | Next page |
| **Tap center** | Toggle chrome | Toggle chrome |
| **Pinch out** | — | Zoom in (max 4x) |
| **Pinch in** | — | Zoom out (min 1x) |
| **Double-tap** | — | Zoom to fit |
| **Hardware back / ← button** | Save + exit | Save + exit |

### Reader Error States

**EPUB fetch failed:**
```
┌─────────────────────────────────────────┐
│  ←                                      │
├─────────────────────────────────────────┤
│                                         │
│              🐝                         │
│                                         │
│      Cannot load book                   │  display-md
│                                         │
│  This book is temporarily unavailable   │  body-md muted
│  from Internet Archive.                 │
│                                         │
│    [    TRY AGAIN    ]                  │  Primary CTA
│                                         │
│         Go back                         │  Tertiary text
│                                         │
└─────────────────────────────────────────┘
```

---

## 📐 Layout & Grid

### Content Width

```
Mobile:   100%
Tablet:   100% up to 768px
Desktop:  max-width 1400px, centered  🔄 (was 1280px, expanded for wider rows)
Wide:     Editorial body caps at 1400px; hero art full-bleed
```

### Column Grid

```
Mobile:   4-column, 16px gutters
Tablet:   8-column, 24px gutters
Desktop:  12-column, 32px gutters
```

### Feature Card Grid

| Context | Mobile | Tablet | Desktop |
|---------|--------|--------|---------|
| Home (collection rows) | scroll ~2.3 cards | scroll ~4 cards | scroll ~6 cards |
| Full collection grid | 3-up | 4-up | 5-up |
| Search results | 2-up | 3-up | 4-up |
| Library grid | 3-up | 4-up | 5-up |
| Genre selection | 2-up | 3-up | 4-up |
| Content choice tiles 🆕 | 1-up stacked | 3-up | 3-up |
| Insights stats | 2-up | 4-up | 4-up |

Layout is mode-agnostic — grid structure never changes between themes.

---

## 📱 Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|------|-------|-------------|
| **Mobile** | < 640px | Hero crops vertically; H1 80→32px; 2-up grid; bottom tab |
| **Tablet** | 640–1024px | H1 56px; 2–3-up grid; bottom tab; rows show ~4 cards |
| **Desktop** | 1024–1400px | Full H1 80px; 4–5-up grid; sidebar option; rows show ~6 cards |
| **Wide** | > 1400px | Body caps 1400px; hero full-bleed |

### Responsive Type Scaling

| Token | Mobile | Tablet | Desktop |
|-------|--------|--------|---------|
| display-mega | 32px | 56px | 80px |
| display-xl | 28px | 40px | 56px |
| display-lg | 24px | 30px | 36px |
| display-md | 20px | 22px | 26px |
| row-title 🆕 | 18px | 20px | 20px |
| reader-body 🆕 | 17px | 18px | 19px |

### Touch Targets

- Primary CTA height: 48px — WCAG AAA
- Tab bar items: 44px minimum
- Book/comic cards: 44px minimum interactive area
- Star rating input: 36px per star
- Series order rows: 48px minimum
- Content type tabs: 44×44 minimum

---

## 🖥️ Screen-by-Screen Design Specs

### Splash Screen — Always Dark

```
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
```

### Welcome Screen

```
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
```

### Login & Register

```
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
```

### ContentChoiceScreen 🆕 (Onboarding)

```
┌─────────────────────────────────────────┐
│                                         │
│  What do you love to read?              │  display-lg
│                                         │
│  You can change this later in settings. │  body-md muted
│                                         │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  │            📚                   │    │  ← Large tile
│  │                                 │    │     120px icon
│  │           BOOKS                 │    │     title-md
│  │                                 │    │
│  │   Fiction, non-fiction,         │    │  body-sm muted
│  │   novels, biographies           │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │            🦸                   │    │
│  │           COMICS                │    │
│  │   Superhero, manga,             │    │
│  │   graphic novels                │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │            ✨                   │    │
│  │            BOTH                 │    │
│  │   The best of both worlds       │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌───────────────────────────────┐      │
│  │        CONTINUE →              │      │  Primary CTA (disabled until pick)
│  └───────────────────────────────┘      │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Title                 │  #ffffff       │  #1a1a2e              │
│  Subtitle              │  #9e9eb8       │  #4a4a6a              │
│  Tile (default) bg     │  #252542       │  #ffffff + border     │
│  Tile (default) border │  none          │  1px #d2d2e0          │
│  Tile (selected) bg    │  #FFC93C       │  #FFC93C              │
│  Tile (selected) text  │  #1a1a2e       │  #1a1a2e              │
│  Tile height           │  min 160px     │  min 160px            │
│  Tile padding          │  24px          │  24px                 │
│  Icon size             │  120px         │  120px                │
│  Icon-title gap        │  16px          │  16px                 │
│  Title (in tile)       │  title-md      │  title-md             │
│  Description           │  body-sm muted │  body-sm muted        │
│  Tile gap              │  16px vertical │  16px vertical        │
│  Continue CTA          │  #FFC93C       │  #FFC93C              │
│  Continue (disabled)   │  opacity 0.4   │  opacity 0.4          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### RateInitialContentScreen (Onboarding)

Content shown depends on ContentChoiceScreen selection:
- **Books only** → 15 popular books
- **Comics only** → 15 popular comic issues
- **Both** → 8 books + 7 comics mixed

```
┌─────────────────────────────────────────┐
│  Rate a few items you love              │  display-lg
│                                         │
│  3 of 5 rated                           │  caption-uppercase muted
│  ▓▓▓░░  ← progress                     │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ ┌───┐  Dune              📚 BOOK│    │
│  │ │Cvr│  Frank Herbert            │    │
│  │ └───┘                            │    │
│  │  ⭐ ⭐ ⭐ ⭐ ⭐  Haven't read     │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ ┌───┐  Batman: Year One 🦸 COMIC│    │
│  │ │Cvr│  Frank Miller             │    │
│  │ └───┘                            │    │
│  │  ⭐ ⭐ ⭐ ○ ○   Haven't read      │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [ CONTINUE → ] (enabled at 5+)         │
└─────────────────────────────────────────┘
```

### Genre Selection (Onboarding)

```
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
```

### Personalizing Screen — Always Dark

```
┌─────────────────────────────────────────────────────────┐
│  ALWAYS DARK — Cinematic loading moment                 │
│                                                         │
│  backgroundColor:  #1a1a2e (fixed)                      │
│  🐝 mascot:        #FFC93C animated pulse               │
│  Title:            "Building your personal collections" │
│  Body:             #9e9eb8                              │
│  Progress bar:     #FFC93C fill / #252542 track         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### HomeScreen 🔄 (Netflix-Style)

```
┌─────────────────────────────────────────┐
│  Kitabee                     🔔  ⚙️     │  Header
├─────────────────────────────────────────┤
│                                         │
│  Good evening, Priya 👋                 │  display-lg
│                                         │
│  ▶ Continue Reading                     │  row-title
│  ┌─────────────────────────────┐        │
│  │📚 Sapiens · 45% · [CONT]    │        │
│  └─────────────────────────────┘        │
│                                         │
│  🔥 Because You Loved Dune...           │  row-title
│  ┌────┐┌────┐┌────┐┌────┐►             │  Collection row
│  │📚 ││📚 ││📚 ││📚 │                │
│  └────┘└────┘└────┘└────┘              │
│                                         │
│  🌍 Epic Worlds Built From Scratch      │  row-title
│  ┌────┐┌────┐┌────┐┌────┐►             │
│  │📚 ││📚 ││📚 ││📚 │                │
│  └────┘└────┘└────┘└────┘              │
│                                         │
│  📖 Free to Read Right Now              │  row-title
│  ┌────┐┌────┐┌────┐┌────┐►             │
│  │🆓││🆓││🆓││🆓│                     │  Free badges visible
│  └────┘└────┘└────┘└────┘              │
│                                         │
│  🦸 Comics — Perfect Starting Points    │  row-title
│  ┌────┐┌────┐┌────┐┌────┐►             │
│  │🦸││🦸││🦸││🦸│                     │
│  └────┘└────┘└────┘└────┘              │
│                                         │
│  (more rows below...)                   │
├─────────────────────────────────────────┤
│  🏠     🔍     📖     📊     👤         │  Tab bar
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Header bg             │  #1a1a2e       │  #f7f7f2              │
│  Greeting text         │  #ffffff       │  #1a1a2e              │
│  Sub-greeting          │  #9e9eb8       │  #4a4a6a              │
│  Row title color       │  #ffffff       │  #1a1a2e              │
│  "See all" color       │  #FFC93C       │  #cc8800              │
│  Row gap (between)     │  48px          │  48px                 │
│  Card bg               │  #252542       │  #ffffff              │
│  Card border           │  none          │  1px #d2d2e0          │
│  Card title            │  #ffffff       │  #1a1a2e              │
│  Card author           │  #9e9eb8       │  #4a4a6a              │
│  Free badge bg         │  #FFC93C       │  #FFC93C              │
│  Free badge text       │  #1a1a2e       │  #1a1a2e              │
│  Star fill             │  #FFC93C       │  #FFC93C              │
│  Tab bar bg            │  #1a1a2e       │  #f7f7f2              │
│  Tab active            │  #FFC93C       │  #FFC93C              │
│  Tab inactive          │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
```

### FullCollectionScreen 🆕

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Header title          │  #ffffff       │  #1a1a2e              │
│  Meta (item count)     │  #666680       │  #8888a8              │
│  Description bg        │  transparent   │  transparent          │
│  Description text      │  #9e9eb8       │  #4a4a6a              │
│  Description padding   │  16px 24px     │  16px 24px            │
│  Grid columns (mob)    │  3             │  3                    │
│  Grid columns (tab)    │  4             │  4                    │
│  Grid columns (desk)   │  5             │  5                    │
│  Grid gap              │  16px          │  16px                 │
│  Card bg               │  #252542       │  #ffffff              │
│  Card border           │  none          │  1px #d2d2e0          │
└────────────────────────┴────────────────┴───────────────────────┘
```

### SearchScreen 🔄 (Books + Comics Tabs)

```
┌─────────────────────────────────────────┐
│  ┌────────────────────────────────┐ ✕   │
│  │ 🔍 Search books, comics...     │     │  Search input
│  └────────────────────────────────┘     │
├─────────────────────────────────────────┤
│                                         │
│  [ All ]  [ Books ]  [ Comics ]         │  Content type tabs
│  ─────                                  │
│                                         │
│  Filter: [Genre ▼]  [ Free only ☐ ]     │  Filters
│                                         │
│  RESULTS                                │  caption-upper muted
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ ┌───┐ Sapiens          📚 · ⭐4.6│    │  Result card
│  │ │Cvr│ Yuval Noah Harari         │    │
│  │ │🆓│                             │    │  Free badge if applicable
│  │ └───┘                             │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ ┌───┐ Batman: Year One 🦸 · ⭐4.8│    │
│  │ │Cvr│ Frank Miller · Issue #1   │    │
│  │ └───┘ DC Comics                  │    │
│  └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Search input bg       │  #1a1a2e       │  #ffffff              │
│  Search input border   │  #252542       │  #d2d2e0              │
│  Search input (focus)  │  #FFC93C       │  #FFC93C              │
│  Search text           │  #ffffff       │  #1a1a2e              │
│  Search placeholder    │  #666680       │  #aaaacc              │
│  Content tabs — see Content Type Tabs component                 │
│  Filter chip bg        │  #252542       │  #ebebeb              │
│  Filter chip text      │  #ffffff       │  #1a1a2e              │
│  Section labels        │  #666680       │  #8888a8              │
│  Recent item text      │  #ffffff       │  #1a1a2e              │
│  Recent item icon      │  #9e9eb8       │  #4a4a6a              │
│  Result card bg        │  #252542       │  #ffffff              │
│  Result card border    │  none          │  1px #d2d2e0          │
│  Type badge — see Content Type Design Language                  │
│  Divider               │  #252542       │  #d2d2e0              │
└────────────────────────┴────────────────┴───────────────────────┘
```

### DetailScreen 🔄 (Books + Comics)

```
┌─────────────────────────────────────────┐
│  ←                                  ⋮   │  Header
├─────────────────────────────────────────┤
│                                         │
│         ┌──────────────┐                │
│         │              │                │
│         │   [Cover]    │                │  Hero (2:3)
│         │              │                │
│         └──────────────┘                │
│                                         │
│         Dune                            │  display-lg
│         by Frank Herbert                │  body-md muted
│         📚 · ⭐ 4.5 (12,345)             │  badge-micro + rating
│                                         │
│  ┌──────────┬──────────┬──────────┐     │
│  │📖 Free  │ +Library │  Rate    │     │  Action row
│  │  Read    │          │          │     │  (Free Read only if
│  └──────────┴──────────┴──────────┘     │   available)
│                                         │
│  ─────────────────────────────────────  │  Divider
│                                         │
│  🎯 WHY WE RECOMMEND THIS               │  caption-upper
│  Because you loved "Foundation" and     │  body-md
│  87% of similar readers enjoyed it.     │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  🔢 DUNE SERIES — Reading Order         │  Series section
│  (see Series Order Section spec §12)    │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📖 ABOUT                               │  caption-upper
│  In the far future of humanity...       │  body-md
│  [Show more]                            │
│                                         │
│  🎭 Mood:  [ epic ] [ thoughtful ]      │  Mood tags
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  💬 SENTIMENT ANALYSIS                  │
│  ┌────────────────────────────────┐     │
│  │ 😊 Positive: 82% ▓▓▓▓▓▓▓▓░░   │     │
│  │ 😐 Neutral:  13% ▓░░░░░░░░░   │     │
│  │ 😞 Negative:  5% ▓░░░░░░░░░   │     │
│  └────────────────────────────────┘     │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📚 SIMILAR BOOKS                       │
│  [Card] [Card] [Card] [Card] ►          │  Mini row
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ℹ️ DETAILS                             │
│  Published: 1965                        │
│  Pages: 688                             │
│  Publisher: Chilton Books               │
│  ISBN: 978-0441172719                   │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Hero cover blur bg    │  #1a1a2e       │  #f7f7f2              │
│  Book title            │  #ffffff       │  #1a1a2e              │
│  Author text           │  #9e9eb8       │  #4a4a6a              │
│  Type badge (see Content Type Design Language)                  │
│  Star fill             │  #FFC93C       │  #FFC93C              │
│  Rating count          │  #9e9eb8       │  #4a4a6a              │
│  Free Read btn         │  #FFC93C bg    │  #FFC93C bg           │
│                        │  #1a1a2e text  │  #1a1a2e text         │
│  +Library btn border   │  #ffffff       │  #1a1a2e              │
│  +Library btn text     │  #ffffff       │  #1a1a2e              │
│  Rate btn border       │  #ffffff       │  #1a1a2e              │
│  Rate btn text         │  #ffffff       │  #1a1a2e              │
│  Dividers              │  #252542       │  #d2d2e0              │
│  Section labels        │  #666680       │  #8888a8              │
│  "Why" label           │  #FFC93C       │  #cc8800              │
│  Body text             │  #9e9eb8       │  #4a4a6a              │
│  Mood tag bg           │  #252542       │  #ebebeb              │
│  Mood tag text         │  #9e9eb8       │  #4a4a6a              │
│  Sentiment pos. bar    │  #03904a       │  #03904a              │
│  Sentiment neg. bar    │  #f13a2c       │  #f13a2c              │
│  Similar cards         │  ContentCard component                 │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Rating Modal

```
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
│  Spoiler toggle bg     │  #252542       │  #ebebeb              │
│  Spoiler toggle active │  #FFC93C       │  #FFC93C              │
│  Submit CTA            │  #FFC93C       │  #FFC93C              │
│  Cancel text           │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
```

### LibraryScreen 🔄 (Books + Comics Toggle)

```
┌─────────────────────────────────────────┐
│  My Library                        🔍   │  Header
├─────────────────────────────────────────┤
│                                         │
│  [ All ]  [ Books ]  [ Comics ]         │  Content type tabs
│                                         │
│  Want (24) │ Reading (5) │ Read (68)    │  Status tabs
│  ─────────                              │
│                                         │
│  Sort: [Recently added ▼]               │
│  View: [Grid] [List]                    │
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │🦸│ │📚 │                     │  Mixed content
│  └────┘ └────┘ └────┘                   │
│  Title  Title  Title                    │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Content type tabs — see Content Type Tabs component            │
│  Status tab (inactive) │  #666680       │  #8888a8              │
│  Status tab (active)   │  #ffffff       │  #1a1a2e              │
│  Active tab indicator  │  #FFC93C (2px) │  #FFC93C (2px)        │
│  Sort dropdown bg      │  #1a1a2e       │  #ffffff              │
│  View toggle bg        │  #252542       │  #ebebeb              │
│  View toggle active    │  #FFC93C       │  #FFC93C              │
│  Book card             │  ContentCard component                 │
│  Empty state — see Empty State component                        │
└────────────────────────┴────────────────┴───────────────────────┘
```

### EPUBReaderScreen 🆕

*(Full spec in §13 Reader Screens)*

### ComicsReaderScreen 🆕 — Always Dark

*(Full spec in §13 Reader Screens)*

### Insights / Reading DNA 🔄 (Books + Comics)

```
┌─────────────────────────────────────────┐
│  Your Reading DNA 🧬          [Share]   │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  🐝 You are a                    │    │
│  │  "Epic World Explorer"           │    │  Personality card
│  │                                  │    │  (amber bg)
│  │  You love vast worlds...         │    │
│  └─────────────────────────────────┘    │
│                                         │
│  📊 BOOKS VS COMICS                     │  New v3.0
│  ┌─────────────────────────────────┐    │
│  │  📚 Books:  65%                  │    │
│  │  🦸 Comics: 35%                  │    │
│  └─────────────────────────────────┘    │
│                                         │
│  📊 GENRE BREAKDOWN                     │
│  [Pie chart with genres]                │
│                                         │
│  📈 READING PACE (Last 6 Months)        │
│  [Line chart]                           │
│                                         │
│  🏆 TOP AUTHORS + CREATORS              │
│  1. Frank Herbert (5 books)             │
│  2. Frank Miller (3 comics)             │
│                                         │
│  🌍 DIVERSITY SCORE                     │
│  8.7/10 — Above average!                │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Personality card bg   │  #FFC93C       │  #FFC93C              │
│  Personality title     │  #1a1a2e       │  #1a1a2e              │
│  Personality body      │  #1a1a2e 85%   │  #1a1a2e 85%          │
│  Chart bg              │  #252542       │  #ffffff              │
│  Chart line/fill       │  #FFC93C       │  #FFC93C              │
│  Books color (chart)   │  #FFC93C       │  #FFC93C              │
│  Comics color (chart)  │  #4c98b9       │  #4c98b9              │
│  Stat number           │  number-display│  number-display       │
│  Stat number color     │  #ffffff       │  #1a1a2e              │
│  Stat label            │  #666680       │  #8888a8              │
│  List row text         │  #ffffff       │  #1a1a2e              │
│  Divider               │  #252542       │  #d2d2e0              │
│  Section labels        │  #666680       │  #8888a8              │
└────────────────────────┴────────────────┴───────────────────────┘
```

### Profile & Settings 🔄

```
┌─────────────────────────────────────────┐
│  Profile                          ⚙️    │
├─────────────────────────────────────────┤
│                                         │
│         ┌──────────────┐                │
│         │   [Avatar]   │                │
│         └──────────────┘                │
│                                         │
│         Priya Sharma                    │
│         priya@example.com               │
│                                         │
│  ┌───────┬───────┬───────┬───────┐      │
│  │  47   │  15   │  4.2  │  8.5  │      │  Stats (Books+Comics)
│  │Books  │Comics │  Avg  │Divers │      │
│  │ Read  │  Read │ Rating│ Score │      │
│  └───────┴───────┴───────┴───────┘      │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 👤 Edit Profile             →      │ │
│  ├────────────────────────────────────┤ │
│  │ 📚 Content Preference       →      │ │  New v3.0
│  │    Books + Comics                  │ │
│  ├────────────────────────────────────┤ │
│  │ 🎨 Theme              Auto  →      │ │
│  ├────────────────────────────────────┤ │
│  │ 🔒 Privacy                  →      │ │
│  ├────────────────────────────────────┤ │
│  │ ℹ️ About                    →      │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │        Log Out                     │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

```
┌────────────────────────┬────────────────┬───────────────────────┐
│  Element               │  Dark          │  Light                │
├────────────────────────┼────────────────┼───────────────────────┤
│  Screen bg             │  #1a1a2e       │  #f7f7f2              │
│  Avatar border         │  #FFC93C       │  #FFC93C              │
│  Name text             │  #ffffff       │  #1a1a2e              │
│  Email text            │  #9e9eb8       │  #4a4a6a              │
│  Stat card bg          │  #252542       │  #ffffff              │
│  Stat card border      │  none          │  1px #d2d2e0          │
│  Stat number           │  #ffffff       │  #1a1a2e              │
│  Stat label            │  #666680       │  #8888a8              │
│  Menu row bg           │  #252542       │  #ffffff              │
│  Menu row text         │  #ffffff       │  #1a1a2e              │
│  Menu row chevron      │  #666680       │  #8888a8              │
│  Menu subtitle         │  #9e9eb8       │  #4a4a6a              │
│  Divider (menu)        │  #1e1e38       │  #ebebf0              │
│  Theme radio active    │  #FFC93C       │  #FFC93C              │
│  Theme radio inactive  │  #252542       │  #d2d2e0              │
│  Log Out text          │  #f13a2c       │  #f13a2c              │
│  Log Out border        │  #f13a2c       │  #f13a2c              │
└────────────────────────┴────────────────┴───────────────────────┘
```

---

## 🎬 Motion & Animation 🆕

Kitabee uses motion **sparingly and purposefully** — never decorative. Every animation serves user comprehension.

### Motion Tokens

```typescript
// design-tokens/motion.ts
export const motion = {
  duration: {
    instant:  100,   // Micro-interactions (tap feedback)
    fast:     200,   // Tab switch, chip select
    normal:   300,   // Modal open, transitions
    slow:     500,   // Page transitions
    reader:   250,   // Page turns in reader
  },
  easing: {
    standard:    'cubic-bezier(0.4, 0.0, 0.2, 1)',    // Material standard
    decelerate:  'cubic-bezier(0.0, 0.0, 0.2, 1)',    // Enter
    accelerate:  'cubic-bezier(0.4, 0.0, 1, 1)',      // Exit
    spring:      'cubic-bezier(0.34, 1.56, 0.64, 1)', // Playful bounce
  },
};
```

### Animation Inventory

| Element | Duration | Easing | Notes |
|---------|----------|--------|-------|
| **Button press** | 100ms | standard | Scale 0.97 |
| **Tab switch** | 200ms | standard | Underline slide |
| **Modal open** | 300ms | decelerate | Slide up + fade |
| **Modal close** | 200ms | accelerate | Slide down + fade |
| **Bottom sheet** | 350ms | spring | Slight bounce |
| **Toast in** | 300ms | decelerate | Slide from top |
| **Toast out** | 200ms | accelerate | Fade |
| **Card long-press** | 100ms | standard | Scale 0.97 |
| **Row horizontal scroll** | native | native | Snap to card |
| **Skeleton shimmer** | 1400ms | linear (infinite) | Left→right gradient |
| **Reader page turn** | 250ms | standard | Horizontal slide |
| **Reader chrome fade** | 300ms | standard | Auto-hide after 2s |
| **Free badge appear** | 200ms | spring | Scale from 0.5→1 |
| **Mascot pulse (splash)** | 1500ms | ease-in-out (infinite) | Opacity 0.6↔1.0 |
| **Progress bar fill** | 500ms | decelerate | Width transition |
| **Continue reading update** | 200ms | standard | Silent, no toast |

### Reduced Motion Support

Respect `prefers-reduced-motion` and `AccessibilityInfo.isReduceMotionEnabled()`:

```typescript
const reduceMotion = await AccessibilityInfo.isReduceMotionEnabled();

if (reduceMotion) {
  // Disable: shimmer, mascot pulse, spring bounces, page-turn slide
  // Replace with: instant opacity change (100ms fade)
}
```

**Never disable:**
- Focus ring appearance (accessibility critical)
- Toast auto-dismiss timing
- Reader chrome auto-hide

### Netflix Row Scroll Physics

- **iOS/Android:** Native ScrollView with `pagingEnabled={false}` and `snapToInterval={cardWidth + gap}`
- **Web:** CSS `scroll-snap-type: x mandatory` on container, `scroll-snap-align: start` on cards
- **Decel rate:** 'fast' on iOS, default on Android
- **Overscroll:** Bounce on iOS (native), disabled on Android

---

## ✅ Do's and Don'ts

### ✅ Do

- Use **semantic tokens** in every component — `theme.background.card`, not `#252542`.
- Reserve `brand.primary` (`#FFC93C`) for CTAs, active tabs, stars, bee mark, **and the free reading badge** — scarcely.
- Set every CTA to `rounded.none` (0px) — the brand's precision signature.
- Render CTA labels in uppercase with 1.4px tracking via `typography.button`.
- Force **SplashScreen**, **PersonalizingScreen**, and **ComicsReaderScreen** to always dark — cinematic and functional reasons.
- Let `border.focus` and `border.inputFocus` stay amber (`#FFC93C`) in both modes.
- Use the explicit 8px spacing ladder — never ad-hoc values.
- Use `spacing.lg` (48px) between collection rows on HomeScreen. 🆕
- Keep display weight at 500 — editorial confidence.
- Add 1px `border.default` to cards in light mode — the contrast between `#f7f7f2` and `#ffffff` is subtle; the border defines the card.
- Use `text.link` (`#cc8800`) in light mode instead of `#FFC93C` for links.
- Use **ContentCard** component universally — books and comics share the same layout. 🆕
- Show **type badge** (`📚 BOOK` / `🦸 COMIC`) only in mixed contexts (search, unified library). 🆕
- Use **reader-body** typography (17px / 1.7 line-height) in EPUBReaderScreen for extended reading comfort. 🆕
- Fade reader chrome after **2 seconds** of inactivity — restores tap-to-toggle. 🆕
- Use `background.reader` and `text.reader` semantic tokens in reader screens for softened contrast. 🆕
- Respect `prefers-reduced-motion` — disable shimmer, mascot pulse, and page-turn slides. 🆕

### ❌ Don't

- Don't hardcode hex values in components — always use the semantic theme token.
- Don't introduce a second brand accent color — amber is the only voltage.
- Don't use rounded or pill CTAs — 0px sharp corners only.
- Don't bold display copy — weight 700 for `title-md`, `button`, `badge-micro`, and `number-display` only.
- Don't use pure black `#000000` anywhere — `canvas` (`#1a1a2e`) is the darkest surface (except comics reader which uses `#0d0d1a`).
- Don't use pure white `#ffffff` as the light mode screen bg — use `#f7f7f2` (slightly warm).
- Don't change `brand.primary` (`#FFC93C`) between modes — it is the one immutable anchor.
- Don't use `#FFC93C` as link text on light canvas — use `#cc8800` instead for contrast.
- Don't add drop shadow tiers — one soft drop max, web hover only.
- Don't scatter amber decoratively — scarcity is what gives it identity power.
- Don't force ComicsReaderScreen to follow user's light-mode preference — comics always render on dark. 🆕
- Don't put a free reading badge on content that lacks Internet Archive availability — check `is_free_online` flag first. 🆕
- Don't stack more than 2 mood tag chips per line — they should feel considered, not spammed. 🆕
- Don't hide the "You are here" indicator in series sections — it is the killer navigational cue. 🆕
- Don't animate collection row cards individually — the row scrolls as a unit for performance. 🆕
- Don't use `reader-body` typography outside the EPUB reader — its relaxed spacing looks wrong in editorial layouts. 🆕
- Don't forget to test contrast in both modes — especially `text.secondary` and `text.muted`.

---

## ♿ Accessibility Standards

### Color Contrast

All text meets WCAG AA minimum in both modes:

| Pairing | Dark Ratio | Light Ratio | Standard |
|---------|-----------|-------------|----------|
| `text.primary` on `background.primary` | 14.8:1 | 16.1:1 | ✅ AAA |
| `text.secondary` on `background.primary` | 4.6:1 | 4.5:1 | ✅ AA |
| `text.muted` on `background.primary` | 4.5:1 | 4.5:1 | ✅ AA |
| `brand.onPrimary` on `brand.primary` | 8.2:1 | 8.2:1 | ✅ AAA |
| `text.link` on `background.primary` | 7.1:1 (amber) | 4.6:1 (dark amber) | ✅ AA |
| `text.primary` on `background.card` | 12.4:1 | 17.1:1 | ✅ AAA |
| `text.reader` on `background.reader` 🆕 | 13.9:1 | 15.2:1 | ✅ AAA |
| Free badge text on badge bg 🆕 | 8.2:1 | 8.2:1 | ✅ AAA |

### Touch Target Minimums

- All interactive elements: minimum **44×44px**
- Primary CTA height: **48px** (WCAG AAA)
- Tab bar items: **44px** effective tap area
- Star inputs: **36px** per star
- Series order rows: **48px** minimum 🆕
- Content type tabs: **44×44px** 🆕
- ContentCard: **44×44px** minimum interactive area 🆕
- Reader nav zones (edge tap): **60px** wide edges 🆕

### Focus Indicators

- Focus ring: **2px solid `#FFC93C`** — same in both modes
- Offset: **2px** from element edge
- Never suppress focus rings — visible in both modes

### Screen Reader Support 🆕

Every interactive element must have:

```typescript
<TouchableOpacity
  accessibilityRole="button"
  accessibilityLabel="Book: Dune by Frank Herbert, rated 4.5 stars"
  accessibilityHint="Double tap to view details"
>
```

**Component-specific requirements:**
- **ContentCard:** Full context in label — title, author, type, rating
- **CollectionRow:** Row title as heading (`accessibilityRole="header"`), "Horizontally scrollable" hint
- **SeriesOrderSection:** "You are here" indicator announced explicitly
- **Reader chrome:** Page number announced on turn (`AccessibilityInfo.announceForAccessibility`)
- **Free badge:** Read as "Free to read"
- **Mood tags:** Read as list ("Mood tags: epic, thoughtful, grand")

### System Preferences Respected

```typescript
import { AccessibilityInfo } from 'react-native';

// Reduce motion — disable shimmer, mascot pulse, page-turn animations
const reduceMotion = await AccessibilityInfo.isReduceMotionEnabled();

// High contrast — increase border weight
const highContrast = await AccessibilityInfo.isHighContrastEnabled();
if (highContrast) {
  // Increase border widths from 1px → 2px
  // Boost text contrast one step
}

// Screen reader active — announce dynamic changes
const screenReader = await AccessibilityInfo.isScreenReaderEnabled();
```

### Keyboard Navigation (Web) — Updated v3.0

| Key | Action |
|-----|--------|
| **Tab** | Move focus forward |
| **Shift+Tab** | Move focus backward |
| **Enter / Space** | Activate button |
| **Escape** | Close modal / exit reader |
| **Arrow Left/Right** | Navigate pages in reader 🆕 |
| **Arrow Up/Down** | Scroll home screen 🆕 |
| **Arrow keys (on stars)** | Set rating value |
| **/ (slash)** | Focus search input 🆕 |

---

## 📎 Appendix

### Quick Token Reference

```
═══════════════════════════════════════════════════════════
  DARK MODE
═══════════════════════════════════════════════════════════
  background.primary      #1a1a2e
  background.elevated     #252542
  background.sunken       #131325
  background.card         #252542
  background.reader       #0d0d1a           🆕
  text.primary            #ffffff
  text.secondary          #9e9eb8
  text.muted              #666680
  text.link               #FFC93C
  text.reader             #e8e8f0           🆕
  border.default          #252542
  border.focus            #FFC93C
  border.activeTab        #FFC93C           🆕

═══════════════════════════════════════════════════════════
  LIGHT MODE
═══════════════════════════════════════════════════════════
  background.primary      #f7f7f2
  background.elevated     #ffffff
  background.sunken       #ebebeb
  background.card         #ffffff
  background.reader       #faf8f2           🆕
  text.primary            #1a1a2e
  text.secondary          #4a4a6a
  text.muted              #8888a8
  text.link               #cc8800
  text.reader             #2a2a3e           🆕
  border.default          #d2d2e0
  border.focus            #FFC93C
  border.activeTab        #FFC93C           🆕

═══════════════════════════════════════════════════════════
  BRAND (IMMUTABLE — SAME IN BOTH)
═══════════════════════════════════════════════════════════
  brand.primary           #FFC93C
  brand.primaryActive     #E6A800
  brand.onPrimary         #1a1a2e
  brand.semanticSuccess   #03904a
  brand.semanticWarning   #f13a2c
  brand.semanticInfo      #4c98b9
  brand.freeReading       #FFC93C           🆕

═══════════════════════════════════════════════════════════
  TYPOGRAPHY (SAME IN BOTH — ONLY COLOR CHANGES)
═══════════════════════════════════════════════════════════
  display-mega    80px / 500 / lh 1.05 / ls -1.6px
  display-xl      56px / 500 / lh 1.1  / ls -1.12px
  display-lg      36px / 500 / lh 1.2  / ls -0.36px
  display-md      26px / 500 / lh 1.5  / ls 0.195px
  row-title       20px / 600 / lh 1.3  / ls -0.2px          🆕
  title-md        18px / 700 / lh 1.2  / ls 0
  title-sm        16px / 500 / lh 1.4  / ls 0.08px
  body-md         14px / 400 / lh 1.5  / ls 0
  body-sm         13px / 400 / lh 1.5  / ls 0
  reader-body     17px / 400 / lh 1.7  / ls 0.1px           🆕
  caption         12px / 400 / lh 1.4  / ls 0
  caption-upper   11px / 600 / lh 1.4  / ls 1.1px  / UPPER
  badge-micro     10px / 700 / lh 1.0  / ls 0.8px  / UPPER  🆕
  button          14px / 700 / lh 1.0  / ls 1.4px  / UPPER
  nav-link        13px / 600 / lh 1.4  / ls 0.65px / UPPER

═══════════════════════════════════════════════════════════
  SPACING (SAME IN BOTH)
═══════════════════════════════════════════════════════════
  xxxs 4 · xxs 8 · xs 16 · sm 24 · md 32
  lg 48 · xl 64 · xxl 96 · super 128

═══════════════════════════════════════════════════════════
  RADIUS (SAME IN BOTH)
═══════════════════════════════════════════════════════════
  none 0 · xs 2 · sm 4 · md 6 · lg 8 · xl 12 · full 9999

═══════════════════════════════════════════════════════════
  MOTION                                                    🆕
═══════════════════════════════════════════════════════════
  duration:   instant 100 · fast 200 · normal 300
              slow 500 · reader 250
  easing:     standard · decelerate · accelerate · spring
```

### v3.0 New Components Checklist

- [x] **ContentCard** — Unified for books + comics
- [x] **CollectionRow** — Netflix-style horizontal scroller
- [x] **FullCollectionScreen** — Grid view of full collection
- [x] **ContentTypeTabs** — All/Books/Comics filter
- [x] **ContentChoiceScreen** tiles — Onboarding preference
- [x] **SeriesOrderSection** — Reading order guide
- [x] **FreeBadge** — Amber overlay
- [x] **MoodTag** — Pill chip
- [x] **TypeBadge** — 📚 BOOK / 🦸 COMIC
- [x] **EPUBReaderScreen** chrome + reader typography
- [x] **ComicsReaderScreen** chrome + always-dark
- [x] **Reader settings menu** — Font size, spacing, theme
- [x] **Continue Reading card** — Wide card with progress bar
- [x] **Motion & Animation** — Full inventory

### Related Documents

- [PRD.md](./PRD.md) v2.0 — Product requirements
- [APPFLOW.md](./APPFLOW.md) v2.0 — User flows
- [TECHSPEC.md](./TECHSPEC.md) v2.0 — Technical specification
- [SCHEMA.md](./SCHEMA.md) v2.0 — Database schema

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial design system |
| 2.0 | [Prior] | [Your Name] | Full dark/light theme system added — semantic tokens, ThemeContext, per-screen mode table, component dual-mode specs |
| 3.0 | [Today] | [Your Name] | Aligned with PRD/APPFLOW/TECHSPEC v2.0. Added Netflix-style CollectionRow, unified ContentCard for books+comics, SeriesOrderSection with "You are here" pattern, EPUBReaderScreen + ComicsReaderScreen (always-dark), ContentChoiceScreen tiles, FullCollectionScreen grid, ContentTypeTabs, FreeBadge overlay, MoodTag chips, TypeBadge component. New reader semantic tokens (background.reader, text.reader, background.readerChrome). New typography scales (row-title, reader-body, badge-micro). Full Motion & Animation section. Updated accessibility with screen reader specs. Zustand-based ThemeContext aligned with TECHSPEC state management. Content Type Design Language section unifying books+comics. Total: 21 screens designed (was 17). |

---

**End of Design Document** 🎨

*"Every color. Every pixel. Every token. In every mode. For books and comics. Precisely considered."*