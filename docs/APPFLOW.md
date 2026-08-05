---

# 🔄 Kitabee — Application Flow Document

> **Document Version:** 2.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Status:** 🟢 Approved for Implementation
> **Related Docs:** [PRD.md](./PRD.md) | [TECHSPEC.md](./TECHSPEC.md) | [SCHEMA.md](./SCHEMA.md)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [App Structure Map](#-app-structure-map)
3. [Global Navigation](#-global-navigation)
4. [Screen Inventory](#-screen-inventory)
5. [Flow 1: First-Time User Onboarding](#-flow-1-first-time-user-onboarding)
6. [Flow 2: Returning User Login](#-flow-2-returning-user-login)
7. [Flow 3: Netflix-Style Discovery (Home)](#-flow-3-netflix-style-discovery-home) 🆕
8. [Flow 4: Search (Books + Comics)](#-flow-4-search-books--comics) 🔄
9. [Flow 5: Detail Page + Series Order](#-flow-5-detail-page--series-order) 🔄
10. [Flow 6: Rating Content](#-flow-6-rating-content)
11. [Flow 7: Personal Library](#-flow-7-personal-library) 🔄
12. [Flow 8: Free Reading (EPUB + Comics)](#-flow-8-free-reading-epub--comics) 🆕
13. [Flow 9: Reading Insights](#-flow-9-reading-insights)
14. [Flow 10: Profile & Settings](#-flow-10-profile--settings)
15. [Screen States](#-screen-states)
16. [Error Handling Flows](#-error-handling-flows)
17. [Empty States](#-empty-states)
18. [Loading States](#-loading-states)
19. [Success States](#-success-states)
20. [Cross-Platform Considerations](#-cross-platform-considerations)
21. [Accessibility Flows](#-accessibility-flows)

---

## 🎯 Overview

### Purpose
This document maps every user journey through Kitabee — from first launch through Netflix-style discovery, series-guided reading, and free public domain content consumption.

### What Changed in v2.0
- **Home screen redesigned** as Netflix-style themed collection rows
- **Onboarding updated** to capture books/comics/both preference
- **Search unified** for books + comics with content-type tabs
- **Detail screen updated** with series order guide section
- **New reading flows** for EPUB books and image-based comics
- **Library updated** to show both books and comics
- **10 flows total** (was 8) — added Netflix Discovery + Free Reading

### Scope
- ✅ All MVP user flows (auth, discovery, ratings, library, insights, reading)
- ✅ Netflix-style themed collection experience
- ✅ Series reading order guide
- ✅ Free reading (EPUB + Comics)
- ✅ All screen states (loading, error, empty, success)
- ✅ Cross-platform behavior (web vs mobile)

### Legend

- 🏠 = Home/Root screens
- 🔐 = Authentication screens
- 📚 = Book-related screens
- 🦸 = Comic-related screens 🆕
- 🎬 = Collection screens 🆕
- 🔢 = Series order screens 🆕
- 📖 = Reading screens 🆕
- ⭐ = Rating screens
- 📊 = Insights screens
- 👤 = Profile screens
- ⚠️ = Error/Edge states
- ✅ = Success states
- 🔄 = Loading states
- 📭 = Empty states

---

## 🗺️ App Structure Map

### High-Level Architecture (Updated v2.0)

```
KITABEE APP
│
├── 🔐 Auth Stack (unauthenticated users)
│   ├── Splash Screen
│   ├── Welcome Screen
│   ├── Login Screen
│   └── Register Screen
│
├── 🚀 Onboarding Stack (first-time users)
│   ├── Onboarding Intro
│   ├── Content Choice (Books / Comics / Both) 🆕
│   ├── Rate Initial Content
│   ├── Genre Selection
│   └── Personalization Loading
│
├── 🏠 Main App (authenticated users)
│   │
│   ├── Bottom Tab Navigator
│   │   ├── 🏠 Home Tab (Netflix rows)
│   │   ├── 🔍 Search Tab (Books + Comics)
│   │   ├── 📖 Library Tab (Books + Comics)
│   │   ├── 📊 Insights Tab
│   │   └── 👤 Profile Tab
│   │
│   ├── Detail Stack (books + comics)
│   │   ├── Detail Screen
│   │   └── Full Collection Screen 🆕
│   │
│   └── Reader Stack 🆕
│       ├── EPUB Reader Screen
│       └── Comics Reader Screen
```

### Navigation Hierarchy

```
Root Navigator (Stack)
    │
    ├── Auth Navigator (Stack) ────► Not authenticated
    │   ├── Splash
    │   ├── Welcome
    │   ├── Login
    │   └── Register
    │
    ├── Onboarding Navigator (Stack) ────► First login only
    │   ├── OnboardingIntro
    │   ├── ContentChoice        🆕 books/comics/both
    │   ├── RateInitialContent   🔄 books or comics based on choice
    │   ├── GenreSelection
    │   └── Personalizing
    │
    ├── Main Navigator (Tabs) ────► Authenticated + Onboarded
    │   ├── Home Tab (Stack)
    │   │   ├── HomeScreen               🔄 Netflix rows
    │   │   ├── FullCollectionScreen     🆕
    │   │   └── DetailScreen             🔄 books or comics
    │   ├── Search Tab (Stack)
    │   │   ├── SearchScreen             🔄 books + comics tabs
    │   │   └── DetailScreen
    │   ├── Library Tab (Stack)
    │   │   ├── LibraryScreen            🔄 books + comics
    │   │   └── DetailScreen
    │   ├── Insights Tab (Stack)
    │   │   └── InsightsScreen
    │   └── Profile Tab (Stack)
    │       ├── ProfileScreen
    │       ├── SettingsScreen
    │       └── EditProfileScreen
    │
    └── Reader Modal Stack 🆕 ────► Free reading
        ├── EPUBReaderScreen
        └── ComicsReaderScreen
```

---

## 🧭 Global Navigation

### Bottom Tab Bar (Main App)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              [Current Screen Content]               │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  🏠      🔍       📖        📊       👤             │
│ Home  Search   Library  Insights  Profile           │
└─────────────────────────────────────────────────────┘
```

**Behavior:**
- Always visible in main app
- Active tab highlighted with primary color (`#FFC93C`)
- Tapping current tab scrolls to top OR goes to root of stack
- Hidden during modal presentations (reader screens)

**Cross-Platform:**

| Feature | Mobile | Web |
|---------|--------|-----|
| Tab bar position | Bottom | Bottom (or left sidebar > 1024px) |
| Tap area | 44x44 min | 44x44 min |
| Long-press menu | ✅ Yes | ❌ No |

### Header Navigation

```
┌─────────────────────────────────────────────────────┐
│  ←  Screen Title              🔍  ⋮                 │
├─────────────────────────────────────────────────────┤
```

**Components:**
- Back button (←) — left side when in stack
- Title — centered on iOS, left-aligned on Android/web
- Actions — right side (search, menu, etc.)

---

## 📱 Screen Inventory (Updated v2.0)

### Complete Screen List

| # | Screen | Purpose | Access | Auth Required | Status |
|---|--------|---------|--------|---------------|--------|
| 1 | **SplashScreen** | Brand reveal, auth check | Auto on launch | ❌ | v1.0 |
| 2 | **WelcomeScreen** | Marketing intro | Auto if not logged in | ❌ | v1.0 |
| 3 | **LoginScreen** | Sign in | From Welcome | ❌ | v1.0 |
| 4 | **RegisterScreen** | Create account | From Welcome | ❌ | v1.0 |
| 5 | **OnboardingIntro** | Explain flow | Auto after register | ✅ | v1.0 |
| 6 | **ContentChoiceScreen** 🆕 | Pick books/comics/both | From intro | ✅ | v2.0 |
| 7 | **RateInitialContentScreen** 🔄 | Rate 5 items | From ContentChoice | ✅ | v2.0 |
| 8 | **GenreSelectionScreen** | Pick favorite genres | From ratings | ✅ | v1.0 |
| 9 | **PersonalizingScreen** | ML loading state | Auto after genres | ✅ | v1.0 |
| 10 | **HomeScreen** 🔄 | Netflix-style collection rows | Main tab | ✅ | v2.0 |
| 11 | **FullCollectionScreen** 🆕 | See all items in a collection | From CollectionRow | ✅ | v2.0 |
| 12 | **SearchScreen** 🔄 | Books + Comics search | Main tab | ❌ | v2.0 |
| 13 | **DetailScreen** 🔄 | Book or Comic full info | From any content tap | ❌ | v2.0 |
| 14 | **RatingModal** | Rate a book/comic | From detail | ✅ | v1.0 |
| 15 | **LibraryScreen** 🔄 | Books + Comics library | Main tab | ✅ | v2.0 |
| 16 | **EPUBReaderScreen** 🆕 | Read free public domain books | From detail "Read Free" | ✅ | v2.0 |
| 17 | **ComicsReaderScreen** 🆕 | Read free public domain comics | From detail "Read Free" | ✅ | v2.0 |
| 18 | **InsightsScreen** | Reading DNA | Main tab | ✅ | v1.0 |
| 19 | **ProfileScreen** | User profile | Main tab | ✅ | v1.0 |
| 20 | **SettingsScreen** | App settings | From Profile | ✅ | v1.0 |
| 21 | **EditProfileScreen** | Edit info | From Profile | ✅ | v1.0 |

**Total: 21 screens (was 18 in v1.0)**

---

## 🚀 Flow 1: First-Time User Onboarding

### Purpose
Convert a new visitor into an active user with personalized Netflix-style home screen within 3 minutes.

### Entry Points
- App launched for first time (no auth token)
- User taps "Get Started" on WelcomeScreen

### Exit Points
- ✅ Success: Land on HomeScreen with Netflix-style personalized collections
- ⚠️ Failure: Back to Welcome (if abandoned)

### Complete Flow Diagram (Updated v2.0)

```
┌─────────────────┐
│  App Launched   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SplashScreen 🔄 │  Duration: 1-2s
│ (Logo + brand)  │  Check: Auth token exists?
└────────┬────────┘
         │
         ▼
       ┌───────────────┐
       │ Token exists? │
       └───┬───────┬───┘
           │ No    │ Yes
           ▼       │
┌─────────────────┐│
│ WelcomeScreen   ││
│ - Logo          ││
│ - Value prop    ││
│ - "Get Started" ││
│ - "Sign in"     ││
└────────┬────────┘│
         │         │
    ┌────┴────┐    │
    │ Signup? │    │
    └─┬─────┬─┘    │
      │ Yes │ No   │
      ▼     │      │
┌──────────┐│      │
│ Register ││      │
└────┬─────┘│      │
     │      │      │
     │      ▼      │
     │ ┌─────────┐ │
     │ │ Login   │ │
     │ └────┬────┘ │
     │      │      │
     │      └──────┼──────► Skip to HomeScreen
     │             │
     ▼             │
┌─────────────────┐│
│Register Success ││
│ + Auto-login    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│OnboardingIntro  ││  3-slide carousel
│"Let's find your ││  - Meet Kit 🐝
│  next favorite" ││  - Netflix-style discovery
│                 ││  - Free reading available
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│ContentChoice 🆕 ││  NEW v2.0
│                 ││  User picks:
│What do you love?││
│                 ││
│ 📚 Books        ││  Single-select tiles
│ 🦸 Comics       ││  Large, tappable
│ ✨ Both         ││
│                 ││
│ [Continue →]    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│Rate Initial 🔄  ││  UPDATED v2.0
│Content:         ││  Content shown depends on
│                 ││  ContentChoice above
│Rate 5 [items]:  ││
│                 ││
│ [Item1] ⭐⭐⭐⭐⭐ ││  Books if books chosen
│ [Item2] ⭐⭐⭐   ││  Comics if comics chosen
│ [Item3] Skip    ││  Mix if both chosen
│                 ││
│ Progress: 3/5   ││
│ [Continue →]    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│Genre Selection  ││
│Pick 3+ genres:  ││
│                 ││
│ 📚 Fiction      ││
│ 🚀 Sci-Fi       ││
│ 🕵️ Mystery      ││
│ 🦸 Superhero    ││  If comics enabled
│ 💔 Romance      ││
│ [12 total...]   ││
│                 ││
│ [Continue →]    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│Personalizing 🔄 ││
│                 ││
│ 🐝              ││
│ Building your   ││  Updated messaging
│ personal        ││  for v2.0
│ collections...  ││
│ ████████░░ 80%  ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│  HomeScreen ✅  │◄┘  Netflix-style home!
│                 │
│ Welcome, Priya! │  - 6+ themed collection rows
│                 │  - "Because you loved X..."
│ Your collections│  - "Free to Read Right Now"
│ are ready! 🎉   │  - Comics rows if enabled
└─────────────────┘
```

### Screen-by-Screen Details (v2.0 Updates)

#### ContentChoiceScreen 🆕 (New in v2.0)
- **Purpose:** Set user's content type preference before rating
- **Elements:**
  - Header: "What do you love to read?"
  - Subheader: "You can change this later in settings"
  - Three large tiles:
    - 📚 **Books** — "Fiction, non-fiction, novels"
    - 🦸 **Comics** — "Superhero, manga, graphic novels"
    - ✨ **Both** — "The best of both worlds"
  - Continue button (disabled until choice made)
- **Actions:**
  - Tap tile → Select
  - Tap Continue → RateInitialContent
- **Backend:** Stored temporarily, saved with preferences on onboarding complete

#### RateInitialContentScreen 🔄 (Updated in v2.0)
- **Purpose:** Solve cold start with content matching user's preference
- **Elements:**
  - Header: "Rate a few [books/comics/items] you love"
  - Progress: "X of 5 rated"
  - Content shown depends on ContentChoice:
    - Books only → 15 popular books
    - Comics only → 15 popular comic issues
    - Both → 8 books + 7 comics mixed
  - Each item: cover, title, author/creator, 5-star input, "Haven't read" skip
  - Continue button (enabled at 5 ratings)
- **Actions:**
  - Tap stars → Set rating
  - Tap "Haven't read" → Next item
  - 5+ ratings → Continue enabled
- **Backend:** POST /api/v1/books/{id}/ratings OR /api/v1/comics/{id}/ratings

---

## 🔐 Flow 2: Returning User Login

### Purpose
Get returning users to their Netflix-style home in under 10 seconds.

*[Flow logic unchanged from v1.0 — Login → Home. Only home screen destination is different (Netflix rows instead of simple recommendation lists).]*

### Login Screen Details

- **Elements:**
  - Back button → Welcome
  - Title: "Welcome back!"
  - Email field
  - Password field with show/hide toggle
  - "Sign In" button
  - "New here? Create account" link
- **Validation:**
  - Email format check
  - Password non-empty
- **Actions:**
  - Submit → API call
  - Success → HomeScreen (skip onboarding if `onboarding_completed=true`)
  - Failure → Error toast with retry
- **Backend:** POST /api/v1/auth/login

---

## 🎬 Flow 3: Netflix-Style Discovery (Home) 🆕

### Purpose
Present personalized themed collection rows that feel exactly like Netflix — familiar, engaging, endlessly scrollable.

### Home Screen Layout (Completely Redesigned v2.0)

```
┌─────────────────────────────────────────┐
│  Kitabee                    🔔  ⚙️      │  Header
├─────────────────────────────────────────┤
│                                         │
│  Good evening, Priya 👋                 │  Greeting
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ ▶ Continue Reading                 │ │  If reading progress exists
│  │                                    │ │
│  │ [Book] ────────                    │ │
│  │ Sapiens - 45% complete             │ │
│  │ ▓▓▓▓▓░░░░░                         │ │  Progress bar
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🔥 Because You Loved Dune...       │ │  PERSONALIZED ROW
│  │                                    │ │
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │  Horizontal scroll
│  │                                    │ │  8-12 items
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🌍 Epic Worlds Built From Scratch  │ │  MOOD-BASED ROW
│  │                                    │ │
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 📖 Free to Read Right Now          │ │  FREE READING ROW
│  │                                    │ │
│  │ [Cover🆓][Cover🆓][Cover🆓][Cover🆓]│ │  Free badges visible
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🦸 Comics — Perfect Starting Point │ │  COMICS ROW
│  │                                    │ │  (if comics enabled)
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ ✅ Complete Series — Start to Fin  │ │  SERIES ROW
│  │                                    │ │
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 💎 Hidden Gems You Will Love       │ │  DISCOVERY ROW
│  │                                    │ │
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🔥 Everyone Is Reading This        │ │  TRENDING ROW
│  │                                    │ │
│  │ [Cover] [Cover] [Cover] [Cover] ►  │ │
│  └────────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│  🏠     🔍     📖     📊     👤         │  Tab bar
└─────────────────────────────────────────┘
```

### Home Screen Flow

```
┌─────────────────┐
│  HomeScreen 🔄  │  Loading state on entry
└────────┬────────┘
         │
         ▼
    [Fetch data]
    GET /api/v1/collections
         │
    ┌────┴────┐
    │Success? │
    └─┬─────┬─┘
      │Yes  │No
      ▼     ▼
┌──────────┐┌──────────────┐
│ Render 6+ ││ Error state  │
│ collection││ + Retry btn  │
│  rows     │└──────────────┘
└────┬─────┘
     │
     ▼
[User Actions]
     │
     ├─► Tap content card ─────► DetailScreen(id, type)
     │
     ├─► Swipe horizontally ───► Scroll within row
     │
     ├─► Tap row title ────────► FullCollectionScreen(name)
     │
     ├─► Pull to refresh ──────► Re-fetch /collections
     │
     ├─► Tap Continue Reading ─► Reader Screen (EPUB or Comics)
     │
     └─► Scroll down ──────────► View more collection rows
```

### Content Card Component (v2.0)

```
┌──────────────┐
│              │
│  📚          │  Cover image (2:3 ratio)
│  [Cover]     │
│  🆓          │  Free badge (if applicable)
├──────────────┤
│ Title        │  1-2 lines truncated
│ Author       │  1 line
│ ⭐ 4.5       │  Kitabee rating
└──────────────┘

On tap: Navigate to DetailScreen
Long press: Quick actions (Add to library, Rate)
```

### Collection Row Component 🆕 (v2.0)

```
Row structure:
┌────────────────────────────────────────┐
│ [Emoji] Catchy Collection Title  See all → │
├────────────────────────────────────────┤
│ [Card] [Card] [Card] [Card] [Card] ►    │
└────────────────────────────────────────┘

Behavior:
- Row title tap → FullCollectionScreen
- Card tap → DetailScreen
- Horizontal scroll with paging
- Lazy load additional cards
- Loading skeleton while data fetches
```

### FullCollectionScreen 🆕 (v2.0)

```
┌─────────────────────────────────────────┐
│  ← Epic Worlds Built From Scratch       │
│  12 books · Updated today               │
├─────────────────────────────────────────┤
│                                         │
│  Immersive fantasy worlds you can       │
│  lose yourself in for weeks             │
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │  3-column grid
│  │Dune│ │WoT │ │NotW│                   │
│  └────┘ └────┘ └────┘                   │
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │
│  └────┘ └────┘ └────┘                   │
│                                         │
└─────────────────────────────────────────┘
```

### Personalization Logic (v2.0)

**"Because You Loved [X]..." row:**
- Generated by Personalizer (KNN collaborative filter)
- X = user's top-rated recent book/comic
- Only shows if user has 5+ ratings

**Mood-based rows (e.g. "Epic Worlds Built From Scratch"):**
- Generated by Collection Engine (KMeans + mood detection)
- Multiple mood rows shown based on user taste
- Rotate to avoid staleness

**"Free to Read Right Now" row:**
- Sourced from Internet Archive (public domain)
- Always present on home screen
- Mix of books and comics if user enabled both

**"Complete Series" row:**
- Series Intelligence identifies completed series
- User hasn't started these series yet
- Filtered by user's genre preferences

**"Comics — Perfect Starting Points" row:**
- Only shown if user enabled comics in preferences
- Beginner-friendly comic entry points
- E.g. Batman: Year One, Watchmen, Persepolis

**"Everyone Is Reading This" row:**
- Trending calculation from recent activity
- Global (not personalized)
- Cached weekly

---

## 🔍 Flow 4: Search (Books + Comics) 🔄

### Purpose
Enable users to find any book OR comic by title, author, character, or ISBN in real-time.

### Search Screen Layout (Updated v2.0)

```
┌─────────────────────────────────────────┐
│  ┌────────────────────────────────┐ ✕   │
│  │ 🔍 Search books, comics...     │     │
│  └────────────────────────────────┘     │
├─────────────────────────────────────────┤
│                                         │
│  [ All ] [ Books ] [ Comics ]           │  Content type tabs 🆕
│  ─────                                  │  Active tab underlined
│                                         │
│  Filter by: [Genre ▼] [Free only ☐]     │  Filters + Free toggle 🆕
│                                         │
│  Popular searches:                      │  Empty state
│  #Fiction #Manga #Superhero #SciFi      │
│                                         │
│  Recent searches:                       │
│  🕐 Sapiens                             │
│  🕐 Batman: Year One                    │  Mix of books + comics
│  🕐 Attack on Titan                     │
│                                         │
├─────────────────────────────────────────┤
```

### Search Flow (Updated v2.0)

```
┌─────────────────┐
│  SearchScreen   │
└────────┬────────┘
         │
    [User types]
         │
    [300ms debounce]
         │
         ▼
    [Show loading]
         │
    [Determine content type from active tab]
         │
    ┌────┴────────────────┐
    │ Which tab active?   │
    └──┬──────────┬───────┬┘
       │ All      │ Books │ Comics
       ▼          ▼       ▼
   [GET /search/all]  [GET /books/search]  [GET /comics/search]
       │          │       │
       └──────┬───┴───────┘
              ▼
       [Try cache]
              │
       ┌──────┴──┐
       │ Cached? │
       └─┬─────┬─┘
         │Yes  │No
         │     ▼
         │ [Fetch from primary API]
         │     │
         │     ▼
         │ [Cache result 30m]
         ▼     │
    [Show results]
         │
    ┌────┴────┐
    │Results? │
    └─┬─────┬─┘
      │Yes  │No
      ▼     ▼
[Display] [Empty state]
      │   "No matches"
      │
      ▼
[User Actions]
      │
      ├─► Tap result ────► DetailScreen(id, type)
      │
      ├─► Change tab ────► Refilter results
      │
      ├─► Toggle Free ───► Filter to free-only items
      │
      ├─► Clear search ──► Reset to empty state
      │
      └─► Scroll ────────► Pagination
```

### Search Result Card (v2.0)

```
┌────────────────────────────────────────┐
│ ┌────┐                                 │
│ │📚 │  Book Title                      │
│ │Cvr│  by Author Name                  │
│ │🆓│  📚 Book · ⭐ 4.5                 │  Type label + rating
│ └────┘  Series: Book 1 of Trilogy       │  Series info if applicable
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ ┌────┐                                 │
│ │🦸│  Comic Title                     │
│ │Cvr│  by Creator Name                 │
│ │  │  🦸 Comic · Issue #1 · ⭐ 4.8    │  Type + issue + rating
│ └────┘  Publisher: DC Comics            │
└────────────────────────────────────────┘

Free badge (🆓) visible when Internet Archive has content
```

### Search States

*[Empty, Loading, Results, Error states unchanged from v1.0 — just include both books and comics]*

---

## 📖 Flow 5: Detail Page + Series Order 🔄

### Purpose
Provide rich content information, enable rating/library, show series reading order guide (killer feature), enable free reading when available.

### Detail Screen Layout (Updated v2.0)

```
┌─────────────────────────────────────────┐
│  ←                                  ⋮   │  Header
├─────────────────────────────────────────┤
│                                         │
│         ┌──────────────┐                │
│         │              │                │
│         │   [Cover]    │                │  Hero section
│         │              │                │
│         └──────────────┘                │
│                                         │
│         Dune                            │  Title
│         by Frank Herbert                │  Author
│         📚 Book · ⭐ 4.5 (12,345)       │  Type + Rating
│                                         │
│  ┌──────────┬──────────┬──────────┐     │
│  │📖 Free  │ +Library │  Rate    │     │  Actions
│  │  Read    │          │          │     │  "Free Read" only if
│  └──────────┴──────────┴──────────┘     │  Internet Archive has it
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  🎯 Why we recommend this               │  AI explanation
│  Based on your love for "Foundation"    │  (if from personalized row)
│  and 87% of similar readers enjoyed it. │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  🔢 DUNE SERIES — Reading Order         │  SERIES ORDER SECTION 🆕
│                                         │  (only if part of series)
│  📖 Main Series:                        │
│  1. Dune ← You are here                 │
│  2. Dune Messiah                        │
│  3. Children of Dune                    │
│  4. God Emperor of Dune                 │
│  5. Heretics of Dune                    │
│  6. Chapterhouse: Dune                  │
│                                         │
│  💡 Tip: Books 1-3 are the core         │
│     trilogy. Books 4-6 are for          │
│     dedicated fans.                     │
│                                         │
│  🔀 Prequel Series (by Brian Herbert):  │
│  1. House Atreides                      │
│  2. House Harkonnen                     │
│  3. House Corrino                       │
│                                         │
│  💡 Read after Book 1 or after all 6.   │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📖 About                               │
│  In the far future of humanity, the     │  Description
│  young Paul Atreides accompanies his    │  Show more/less
│  family to the desert planet Arrakis... │
│                                         │
│  🎭 Mood: epic · thoughtful · grand     │  Mood tags 🆕
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  💬 Sentiment Analysis                  │
│  ┌────────────────────────────────┐     │
│  │ 😊 Positive: 82%               │     │
│  │ 😐 Neutral:  13%               │     │
│  │ 😞 Negative:  5%               │     │
│  └────────────────────────────────┘     │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📚 Similar Books                       │
│  [Book1] [Book2] [Book3] [Book4] ►      │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ℹ️ Details                             │
│  Published: 1965                        │
│  Pages: 688                             │
│  Publisher: Chilton Books               │
│  ISBN: 978-0441172719                   │
│                                         │
└─────────────────────────────────────────┘
```

### Detail Screen Flow (Updated v2.0)

```
┌─────────────────────┐
│ DetailScreen 🔄     │
│ (books or comics)   │
└──────────┬──────────┘
           │
           ▼
      [Fetch content data]
      GET /books/{id} OR /comics/{id}
           │
       ┌───┴────┐
       │Cached? │
       └─┬────┬─┘
         │Yes │No
         │    ▼
         │ [Fetch from API]
         │    │
         │    ▼
         │ [Cache 24h]
         ▼    │
      ┌──────┘
      ▼
   [Fetch related in parallel]
   ├─ GET /books/{id}/series or /comics/{id}/series
   ├─ Similar items
   ├─ User rating (if any)
   ├─ Reading progress (if any)
   └─ Free reading availability
      │
      ▼
   [Render screen with sections]
   ├─ Series Order (if is_series)
   ├─ Free Read button (if is_free_online)
   └─ All standard sections
      │
      ▼
[User Actions]
      │
      ├─► Tap "Free Read" 🆕 ──► ReaderScreen (EPUB or Comics)
      │
      ├─► Tap "+ Library" ────► Library modal
      │                         │
      │                         ├─ Want to Read
      │                         ├─ Currently Reading
      │                         └─ Read
      │
      ├─► Tap "Rate" ──────────► RatingModal
      │
      ├─► Tap series entry ────► New DetailScreen for that entry
      │
      ├─► Tap similar item ────► New DetailScreen
      │
      └─► Tap "Show more" ─────► Expand description
```

### Series Order Section 🆕 (v2.0)

**Data source:** GET /api/v1/books/{id}/series or /api/v1/comics/{id}/series

**Rendering rules:**
- Only shown if content is part of a detected series
- "You are here" indicator on current entry
- "Start Here" label on first main entry
- "Prequel" / "Spinoff" labels where applicable
- Tips shown for complex universes
- Companion series (prequels, spinoffs) shown separately
- Each entry is tappable → navigates to that entry's detail page

**Example variations:**

```
Simple trilogy:
🔢 LORD OF THE RINGS
1. The Fellowship of the Ring ← You are here
2. The Two Towers
3. The Return of the King

Complex universe (comics):
🔢 BATMAN — Where To Start
📖 New Reader Path:
1. Batman: Year One ← You are here
2. The Long Halloween
3. The Dark Knight Returns

📖 Complete Path:
1. Batman: Year One
2. Batman: The Killing Joke
3. Knightfall
...
💡 Tip: DC continuity is complex.
        These are standalone-friendly picks.
```

---

## ⭐ Flow 6: Rating Content

### Purpose
Enable users to rate books and comics on a 5-star scale with optional review.

*[Flow logic unchanged from v1.0 — same modal, same UX. Just works for both books and comics now.]*

### Rating Modal Flow

```
┌────────────────────────┐
│    Rate this [book]    │
├────────────────────────┤
│                        │
│  How would you rate    │
│  "Dune"?               │
│                        │
│    ⭐ ⭐ ⭐ ⭐ ⭐       │
│                        │
│  ┌──────────────────┐  │
│  │ Add a review     │  │  Optional
│  │ (optional)       │  │
│  └──────────────────┘  │
│                        │
│  ☐ Contains spoilers   │  Toggle 🆕
│                        │
│  ┌──────────────────┐  │
│  │    Submit        │  │
│  └──────────────────┘  │
│                        │
│         Cancel         │
└────────────────────────┘

Flow:
[Tap stars] → [Optional review] → [Optional spoiler flag] → [Submit]
                                                              │
                                                              ▼
                                                    [POST /ratings]
                                                    (books or comics)
                                                              │
                                                       ┌──────┴──────┐
                                                       │  Success?   │
                                                       └─┬─────────┬─┘
                                                         │Yes      │No
                                                         ▼         ▼
                                                    [Success   [Error toast]
                                                     toast]
                                                         │
                                                         ▼
                                                    [Modal closes]
                                                         │
                                                         ▼
                                                    [Home collections
                                                     refresh async]
```

---

## 📚 Flow 7: Personal Library 🔄

### Purpose
Let users organize books AND comics into meaningful categories.

### Library Screen Layout (Updated v2.0)

```
┌─────────────────────────────────────────┐
│  My Library                        🔍   │  Header
├─────────────────────────────────────────┤
│                                         │
│  [ All ] [ Books ] [ Comics ]           │  Content type toggle 🆕
│                                         │
│  Want (24) │ Reading (5) │ Read (68)    │  Status tabs
│  ─────────                              │
│                                         │
│  Sort by: [Recently added ▼]            │
│  View: [Grid] [List]                    │
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │🦸│ │📚 │                     │  Books + comics mixed
│  │Cvr│ │Cvr│ │Cvr│                     │  (or filtered by type)
│  └────┘ └────┘ └────┘                   │
│  Title  Title  Title                    │
│                                         │
└─────────────────────────────────────────┘
```

### Library Flow (Updated v2.0)

```
┌─────────────────┐
│ LibraryScreen   │
└────────┬────────┘
         │
         ▼
    [Determine active content filter]
    [Determine active status tab]
         │
         ▼
    [Load library based on filters]
    ├─ GET /library?status={status}
    ├─ GET /comics/library?status={status}
    └─ Merge if "All" content type selected
         │
    ┌────┴────┐
    │ Empty?  │
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  [Show grid]
      │
      ▼
┌──────────────────┐
│  Empty state 📭  │  "Your library is empty"
│  🐝              │  "Start by rating books or comics!"
│  [Explore]       │  CTA → HomeScreen
└──────────────────┘

[User Actions]
      │
      ├─► Change content type ──► Refilter (books/comics/all)
      │
      ├─► Change status tab ────► Refilter by status
      │
      ├─► Tap item ─────────────► DetailScreen
      │
      ├─► Long press ───────────► Quick actions
      │                            ├─ Move status
      │                            └─ Remove
      │
      ├─► Change sort ──────────► Re-order list
      │
      └─► Toggle view ──────────► Grid ↔ List
```

---

## 📖 Flow 8: Free Reading (EPUB + Comics) 🆕

### Purpose
Enable users to read public domain books and comics directly inside the app via Internet Archive.

### Free Reading Entry Points

- Tap "Free Read" button on DetailScreen (books or comics)
- Tap "Continue Reading" row item on HomeScreen
- Tap item in "Free to Read Right Now" collection row

### Free Reading Flow (Books)

```
┌─────────────────┐
│  DetailScreen   │  User on book detail
└────────┬────────┘
         │
    [Tap "Free Read"]
         │
         ▼
    [Fetch reading link]
    GET /api/v1/reading/{book_id}/link
         │
    ┌────┴────┐
    │Success? │
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  [Error toast]
      │  "Content unavailable"
      ▼
┌─────────────────────┐
│ EPUBReaderScreen 🆕 │
│                     │
│ ┌─────────────────┐ │
│ │                 │ │
│ │  [Book content  │ │  EPUB rendered
│ │   in WebView    │ │  via EPUB.js
│ │   using EPUB.js]│ │
│ │                 │ │
│ │                 │ │
│ └─────────────────┘ │
│                     │
│ Progress: 45%       │  Progress bar
│ [◄]  Chapter 5  [►] │  Navigation
└──────────┬──────────┘
           │
    [User reads, swipes pages]
           │
    [EPUB.js posts progress via postMessage]
           │
           ▼
    [Debounced 5s]
    PATCH /api/v1/reading/{book_id}/progress
           │
           ▼
    [Progress saved]
           │
    [User exits]
           │
           ▼
    [Return to DetailScreen or Home]
    [Continue Reading row updated]
```

### EPUB Reader Screen 🆕

```
┌─────────────────────────────────────────┐
│  ←  Dune                          ⚙️    │  Header
├─────────────────────────────────────────┤
│                                         │
│                                         │
│  Chapter 5: Arrakis                     │
│                                         │
│  The Duke Leto stood at the balcony     │
│  overlooking the vast desert. His son   │
│  Paul stood beside him, taking in the   │
│  sight of their new home for the first  │
│  time...                                │
│                                         │
│  [Story text rendered by EPUB.js]       │
│                                         │
│  [Long body of text with proper         │
│   typography, spacing, font choice]     │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│  [◄ Prev]  Ch 5 · 45%  [Next ►]         │  Nav + Progress
└─────────────────────────────────────────┘

Gestures:
- Swipe left/right → Page turn
- Tap left edge → Previous page
- Tap right edge → Next page
- Tap center → Show/hide UI chrome
- Back button → Save + exit
```

### Free Reading Flow (Comics)

```
┌─────────────────┐
│  DetailScreen   │  User on comic detail
└────────┬────────┘
         │
    [Tap "Free Read"]
         │
         ▼
    [Fetch reading link]
    GET /api/v1/reading/{comic_id}/link
         │
    ┌────┴────┐
    │Success? │
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  [Error toast]
      ▼
┌─────────────────────┐
│ ComicsReaderScreen  │
│  🆕                 │
│ ┌─────────────────┐ │
│ │                 │ │
│ │                 │ │
│ │  [Comic page    │ │  Image rendered
│ │   image from    │ │  full screen
│ │   Internet      │ │
│ │   Archive]      │ │
│ │                 │ │
│ │                 │ │
│ └─────────────────┘ │
│                     │
│    Page 5 of 32     │  Page indicator
└──────────┬──────────┘
           │
    [User swipes]
           │
           ▼
    [Load next/prev page image]
    [Pre-load 2 pages ahead]
           │
           ▼
    [Update progress on page change]
    PATCH /reading/{comic_id}/progress
           │
    [User exits]
           │
           ▼
    [Return to DetailScreen or Home]
```

### Comics Reader Screen 🆕

```
┌─────────────────────────────────────────┐
│  ←  Batman: Year One            ⚙️      │  Header (fades)
├─────────────────────────────────────────┤
│                                         │
│                                         │
│                                         │
│         [FULL PAGE IMAGE]               │  Comic page image
│                                         │  (full-screen)
│                                         │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│           Page 5 of 32                  │  Fades after 2s
└─────────────────────────────────────────┘

Gestures:
- Swipe left → Next page
- Swipe right → Previous page
- Pinch → Zoom
- Double tap → Zoom to fit
- Tap center → Show/hide UI chrome
- Back button → Save + exit
```

---

## 📊 Flow 9: Reading Insights

### Purpose
Show users their unique reading personality through beautiful data visualizations covering both books and comics.

### Insights Screen Layout (Updated v2.0)

```
┌─────────────────────────────────────────┐
│  Your Reading DNA 🧬          [Share]   │  Header
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  🐝 You are a                      │ │  Personality
│  │  "Epic World Explorer"             │ │
│  │                                    │ │
│  │  You love vast worlds, complex     │ │
│  │  narratives, and diving deep       │ │
│  │  into series universes.            │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📊 Books vs Comics                     │  NEW v2.0
│  ┌────────────────────────────────────┐ │
│  │  📚 Books:  65%                    │ │
│  │  🦸 Comics: 35%                    │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📊 Genre Breakdown                     │
│  ┌────────────────────────────────────┐ │
│  │      Pie chart                     │ │
│  │      Fiction 40%                   │ │
│  │      Sci-Fi 30%                    │ │
│  │      Superhero 15%                 │ │
│  │      Non-fic 15%                   │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📈 Reading Pace (Last 6 Months)        │
│  ┌────────────────────────────────────┐ │
│  │  [Line chart]                      │ │
│  └────────────────────────────────────┘ │
│                                         │
│  🏆 Top Authors + Creators              │
│  1. Frank Herbert (5 books)             │
│  2. Frank Miller (3 comics)             │
│  3. Brandon Sanderson (2 books)         │
│                                         │
│  🌍 Diversity Score                     │
│  ┌────────────────────────────────────┐ │
│  │  8.7/10                            │ │
│  │  Above average!                    │ │
│  └────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Insights Flow

*[Same as v1.0 — needs 10+ rated items to unlock]*

---

## 👤 Flow 10: Profile & Settings

### Profile Screen Layout (Updated v2.0)

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
│  ┌───────┬───────┬───────┬───────┐      │  Stats (Updated v2.0)
│  │  47   │  15   │  4.2  │  8.5  │      │
│  │Books  │Comics │  Avg  │Divers │      │  Books + Comics separate
│  │ Read  │  Read │ Rating│ Score │      │
│  └───────┴───────┴───────┴───────┘      │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 👤 Edit Profile             →      │ │
│  ├────────────────────────────────────┤ │
│  │ 📚 Content Preference       →      │ │  NEW v2.0
│  │    Books + Comics                  │ │  Books/Comics/Both toggle
│  ├────────────────────────────────────┤ │
│  │ 🎨 Theme              Light  →     │ │
│  ├────────────────────────────────────┤ │
│  │ 🔒 Privacy                  →      │ │
│  ├────────────────────────────────────┤ │
│  │ ℹ️ About                    →      │ │
│  ├────────────────────────────────────┤ │
│  │ ❓ Help & Support           →      │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │        Log Out                     │ │
│  └────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Settings Flow

*[Same as v1.0 with added Content Preference option]*

---

## 🎬 Screen States

*[Unchanged from v1.0 — same 4 states: Loading, Success, Error, Empty]*

---

## ⚠️ Error Handling Flows

### Error Types & Responses (Updated v2.0)

| Error Type | Detection | User Sees | Action |
|------------|-----------|-----------|--------|
| **Network offline** | fetch fails | Offline banner | Auto-retry when online |
| **API timeout** | 30s timeout | "Taking longer than expected" | Retry button |
| **401 Unauthorized** | Token invalid | Silent redirect to Login | Auto-logout |
| **404 Not Found** | Resource missing | "Content not found" | Back button |
| **500 Server Error** | Backend crash | "Something went wrong" | Retry button |
| **Rate limit (429)** | Too many requests | "Slow down!" | Countdown |
| **EPUB fetch failed** 🆕 | Timeout on IA | "Cannot load book" | Retry / Skip |
| **Comic image failed** 🆕 | Image load error | "Cannot load page" | Retry / Next page |
| **Collection API failed** 🆕 | ML error | Show fallback popular row | Silent degradation |

### Free Reading Error Handling

```
User taps "Free Read"
         │
         ▼
    [Fetch link]
         │
    ┌────┴────┐
    │Success? │
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  [Toast: "Content temporarily unavailable"]
      │  [Stay on DetailScreen]
      │
      ▼
    [Load reader]
         │
    ┌────┴────┐
    │Loaded?  │
    └─┬─────┬─┘
      │Yes  │No (EPUB fails)
      │     ▼
      │  [Error screen with Retry button]
      │  [Back button visible]
      ▼
    [User reads]
         │
    ┌────┴────┐
    │Page     │
    │loads?   │
    └─┬─────┬─┘
      │Yes  │No (Comics page fails)
      │     ▼
      │  [Show "Loading..." with skip option]
      │  [Auto-retry once]
      ▼
    [Continue reading]
```

---

## 📭 Empty States

### When Empty States Appear (Updated v2.0)

| Screen | Empty Condition | CTA |
|--------|-----------------|-----|
| **Home** | No collections yet (new user) | "Rate 5 items to unlock personalized" |
| **Search** | No results | "Try different keywords" |
| **Library (Books)** | No books | "Explore books" |
| **Library (Comics)** 🆕 | No comics | "Explore comics" |
| **Library (Any status)** | Empty status tab | Contextual CTA |
| **Insights** | < 10 rated items | "Rate 10 items to unlock" |
| **Continue Reading** 🆕 | No reading in progress | Row hidden entirely |

*[Empty state template unchanged from v1.0]*

---

## 🔄 Loading States

*[Unchanged from v1.0 — same 5 patterns]*

### Additional v2.0 Loading States

**Netflix Home Loading:**
- Show skeleton rows (3-4 skeleton collection rows)
- Each skeleton = title placeholder + card placeholders
- Shimmer animation

**Reader Loading:**
- EPUB: Progress bar as EPUB.js loads
- Comics: Skeleton box where image will render + spinner

---

## ✅ Success States

*[Unchanged from v1.0]*

### v2.0 Additions

**Reading Progress Saved:**
- Silent (no toast) — auto-save every 5 seconds
- Toast only if manually saved via menu

**Free Book Downloaded:**
- Toast: "Ready to read!"
- Immediate reader open

---

## 🌐 Cross-Platform Considerations

### Platform-Specific Behaviors (Updated v2.0)

| Feature | Web | iOS | Android |
|---------|-----|-----|---------|
| **Back navigation** | Browser back | Swipe from edge | Hardware back |
| **Pull to refresh** | ❌ | ✅ | ✅ |
| **Haptic feedback** | ❌ | ✅ | ✅ (limited) |
| **Share sheet** | Web Share API | Native | Native |
| **EPUB Reader** 🆕 | iframe with EPUB.js | WebView | WebView |
| **Comics Reader** 🆕 | HTML image swipe | FlatList | FlatList |
| **Full-screen reading** 🆕 | Fullscreen API | Auto | Auto |
| **Pinch to zoom** 🆕 | CSS transform | Gesture | Gesture |

### Responsive Breakpoints

```
Mobile:   0 - 767px       (single column, collection rows scroll horizontally)
Tablet:   768 - 1023px    (2-column grid in library, larger cards)
Desktop:  1024px+         (3-4 cards visible in each row, max-width 1400px)
```

---

## ♿ Accessibility Flows

### Screen Reader Support (Updated v2.0)

**Every interactive element has:**
- Accessibility label (e.g. "Book: Dune by Frank Herbert, rated 4.5 stars")
- Accessibility hint (e.g. "Double tap to view details")
- Accessibility role (button, link, etc.)

**Collection rows:**
- Row title read as heading
- "Horizontally scrollable" hint
- Each card gets full context

**Reader screens:**
- Page number announced on turn
- Progress percentage available
- EPUB text fully accessible via screen reader

### Keyboard Navigation (Web) — Updated v2.0

- **Tab** — Move focus forward
- **Shift+Tab** — Move focus backward
- **Enter/Space** — Activate button
- **Esc** — Close modal / exit reader
- **Arrow Left/Right** — Navigate pages in reader 🆕
- **Arrow Up/Down** — Scroll home screen 🆕

### Color Contrast

All text meets WCAG AA:
- Normal text: 4.5:1 ratio
- Large text: 3:1 ratio
- Interactive elements: 3:1 ratio
- Free reading badge: high contrast yellow on cover overlay

---

## 📎 Appendix

### Related Documents

- [PRD.md](./PRD.md) v2.0 — Product requirements
- [TECHSPEC.md](./TECHSPEC.md) v2.0 — Technical specification
- [SCHEMA.md](./SCHEMA.md) v2.0 — Database schema
- [IMPLEMENTATIONPLAN.md](./IMPLEMENTATIONPLAN.md) v2.0 — Daily plan

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial app flow document |
| 2.0 | [Today] | [Your Name] | Redesigned home as Netflix-style collection rows. Added ContentChoice onboarding step. Added FullCollectionScreen. Added SeriesOrderSection to detail. Added EPUBReaderScreen and ComicsReaderScreen. Updated Library for books + comics. Updated Search with content type tabs. Updated Insights for books + comics. 21 screens total (was 18). 10 flows (was 8). |

---

**End of App Flow Document** 🔄

*"Every tap. Every screen. Every collection row. Every page turned. Documented."*

---
